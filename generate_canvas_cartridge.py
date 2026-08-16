#!/usr/bin/env python3
"""Generate a Canvas Common Cartridge 1.1 (.imscc) for the COMM C1000 course.

Single source of truth is course_data.py. This script derives the module
structure, pages, native assignments, and the weekly audio touchpoints (via
the $IMS-CC-FILEBASE$ substitution token Canvas rewrites on import) from it,
so the whole course imports in one step with working audio.

Usage:
  python3 generate_canvas_cartridge.py [theme] [outfile]
Defaults: theme=Warm_Editorial, outfile=COMM_C1000_Course_Export.imscc
"""

import html
import os
import re
import sys
import zipfile

import course_data as cd

BASE = os.path.dirname(os.path.abspath(__file__))
THEME = sys.argv[1] if len(sys.argv) > 1 else "Warm_Editorial"
OUTFILE = sys.argv[2] if len(sys.argv) > 2 else "COMM_C1000_Course_Export.imscc"
PAGES_DIR = os.path.join(BASE, "Individual_Pages", THEME)
AUDIO_DIR = os.path.join(BASE, "Audio_Assets")
FILEBASE = "$IMS-CC-FILEBASE$/"

MANIFEST_ID = "ia354247de9dd40634bfe9604cc725b1e"
COURSE_ID = "commc1000publicspeakingf26"

RUBRIC_BY_SLUG = {r["slug"]: r for r in cd.RUBRICS}
ASSIGNMENT_BY_SLUG = {a["slug"]: a for a in cd.ASSIGNMENTS}
DISCUSSION_BY_SLUG = {d["slug"]: d for d in cd.DISCUSSIONS}
WEEK_BY_NUM = {w["week"]: w for w in cd.WEEKS}


def esc(s):
    return html.escape(s or "", quote=True)


def read_source(stem):
    path = os.path.join(PAGES_DIR, stem + ".html")
    if not os.path.exists(path):
        raise FileNotFoundError("missing source page: %s" % path)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def extract_parts(text):
    """Return (title, styles, body) from a standalone themed HTML doc."""
    m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    title = html.unescape(m.group(1)).strip() if m else ""
    styles = "".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S | re.I))
    bm = re.search(r"<body[^>]*>(.*)</body>", text, re.S | re.I)
    body = bm.group(1) if bm else text
    return title, styles, body


def strip_pts(title):
    return re.sub(r"\s*\(\d+\s*pts\)\s*$", "", title).strip()


def resolve_one(spec):
    """Resolve a module item spec to (kind, stem, rid, points, title)."""
    kind = spec[0]
    if kind == "week":
        w = WEEK_BY_NUM[spec[1]]
        stem = "Week_%02d_Overview" % w["week"]
        return ("wiki", stem, "week_%02d" % w["week"], None, None)
    if kind == "rubric":
        r = RUBRIC_BY_SLUG[spec[1]]
        return ("wiki", r["filename"][:-5], "rubric_" + r["slug"], None, None)
    if kind == "assignment":
        a = ASSIGNMENT_BY_SLUG[spec[1]]
        return ("assignment", a["filename"][:-5], "asg_" + a["slug"], a["points"], strip_pts(a["title"]))
    if kind == "discussion":
        d = DISCUSSION_BY_SLUG[spec[1]]
        return ("wiki", d["filename"][:-5], "disc_" + d["slug"], None, None)
    if kind == "page":
        override = spec[2] if len(spec) > 2 else None
        return ("wiki", spec[1], "page_" + spec[1].lower(), None, override)
    raise ValueError("unknown module item kind: %r" % (spec,))


def resolve_modules():
    """Resolve MODULES into (title, [(kind, stem, rid, points, title), ...])."""
    resolved = []
    for mtitle, specs in cd.MODULES:
        mod_items = []
        for spec in specs:
            kind, stem, rid, points, title = resolve_one(spec)
            if title is None:
                text = read_source(stem)
                m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
                title = html.unescape(m.group(1)).strip() if m else rid
            mod_items.append((kind, stem, rid, points, title))
        resolved.append((mtitle, mod_items))
    return resolved


def build():
    out = os.path.join(BASE, OUTFILE)
    resolved = resolve_modules()
    audio_files = set()
    wiki_files, asg_files = {}, {}

    for _mtitle, mod_items in resolved:
        for kind, stem, rid, points, title in mod_items:
            _t, styles, body = extract_parts(read_source(stem))
            body, refs = rewire_audio(body)
            audio_files.update(refs)
            if kind == "assignment":
                asg_files[rid] = ASSIGNMENT_XML.format(
                    rid=esc(rid),
                    title=esc(title),
                    content=esc("<style>%s</style>%s" % (styles, body)),
                    points=points,
                )
            else:
                wiki_files[rid] = WIKI_PAGE.format(
                    title=esc(title), rid=esc(rid), styles=styles, body=body,
                )

    # Syllabus (same style pipeline as pages).
    _st, syl_styles, syl_body = extract_parts(read_source("Syllabus"))
    syl_body, syl_refs = rewire_audio(syl_body)
    audio_files.update(syl_refs)
    syllabus_html = ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" "
                     "content=\"text/html; charset=utf-8\">\n<title>Syllabus</title>\n</head>\n<body>\n"
                     "<style>%s</style>\n%s\n</body>\n</html>\n" % (syl_styles, syl_body))

    # Manifest organizations + module_meta + resources.
    org_items, meta_modules, resources = [], [], [RES_SYLLABUS, RES_CANVAS_EXPORT]
    item_id = 0
    for mi, (mtitle, mod_items) in enumerate(resolved):
        mod_id = "module_%02d" % mi
        inner_org, inner_meta = [], []
        for pos, (kind, _stem, rid, _points, title) in enumerate(mod_items, 1):
            iid = "item_%03d" % item_id
            item_id += 1
            ctype = "Assignment" if kind == "assignment" else "WikiPage"
            inner_org.append(
                '      <item identifier="%s" identifierref="%s">\n'
                '        <title>%s</title>\n      </item>' % (esc(iid), esc(rid), esc(title))
            )
            rtype = "assignment_xmlv1p2" if kind == "assignment" else "webcontent"
            rfile = "assignments/%s.xml" % rid if kind == "assignment" else "wiki_content/%s.html" % rid
            resources.append(
                '    <resource identifier="%s" type="%s" href="%s">\n'
                '      <file href="%s"/>\n    </resource>' % (esc(rid), rtype, rfile, rfile)
            )
            inner_meta.append(
                '      <item identifier="%s">\n'
                '        <content_type>%s</content_type>\n'
                '        <workflow_state>active</workflow_state>\n'
                '        <title>%s</title>\n'
                '        <identifierref>%s</identifierref>\n'
                '        <position>%d</position>\n'
                '        <new_tab></new_tab>\n'
                '        <indent>0</indent>\n      </item>'
                % (esc(iid), ctype, esc(title), esc(rid), pos)
            )
        org_items.append(
            '    <item identifier="%s">\n      <title>%s</title>\n%s\n    </item>'
            % (esc(mod_id), esc(mtitle), "\n".join(inner_org))
        )
        meta_modules.append(
            '  <module identifier="%s">\n'
            '    <title>%s</title>\n'
            '    <workflow_state>active</workflow_state>\n'
            '    <position>%d</position>\n'
            '    <require_sequential_progress>false</require_sequential_progress>\n'
            '    <items>\n%s\n    </items>\n  </module>'
            % (esc(mod_id), esc(mtitle), mi + 1, "\n".join(inner_meta))
        )

    # Audio resources (referenced files only).
    for name in sorted(audio_files):
        resources.append(
            '    <resource identifier="res_audio_%s" type="webcontent" href="web_resources/%s">\n'
            '      <file href="web_resources/%s"/>\n    </resource>'
            % (esc(sanitize_id(name)), esc(name), esc(name))
        )

    manifest = MANIFEST.format(
        manifest_id=MANIFEST_ID,
        course_title=esc(cd.COURSE["title"]),
        org_items="\n".join(org_items),
        resources="\n".join(resources),
    )
    module_meta = MODULE_META.format(modules="\n".join(meta_modules))

    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("imsmanifest.xml", manifest)
        z.writestr("course_settings/module_meta.xml", module_meta)
        z.writestr("course_settings/course_settings.xml", COURSE_SETTINGS)
        z.writestr("course_settings/files_meta.xml", FILES_META)
        z.writestr("course_settings/canvas_export.txt", CANVAS_EXPORT_TXT)
        z.writestr("course_settings/syllabus.html", syllabus_html)
        for rid, content in wiki_files.items():
            z.writestr("wiki_content/%s.html" % rid, content)
        for rid, content in asg_files.items():
            z.writestr("assignments/%s.xml" % rid, content)
        for name in sorted(audio_files):
            src = os.path.join(AUDIO_DIR, name)
            if not os.path.exists(src):
                raise FileNotFoundError("referenced audio missing: %s" % src)
            z.write(src, "web_resources/%s" % name)

    return out, resolved, audio_files


def rewire_audio(body):
    """Replace local Audio_Assets srcs with $IMS-CC-FILEBASE$/name; return (body, names)."""
    names = set()
    pattern = re.compile(r'src="(?:\.\./)*Audio_Assets/([^"]+)"')

    def repl(m):
        names.add(m.group(1))
        return 'src="%s%s"' % (FILEBASE, m.group(1))

    return pattern.sub(repl, body), names


def sanitize_id(name):
    # Keep the extension so mp3 and m4a of the same touchpoint get distinct ids.
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def validate(out):
    import collections
    import xml.etree.ElementTree as ET
    errors = []
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
        manifest_xml = z.read("imsmanifest.xml").decode("utf-8")
        module_xml = z.read("course_settings/module_meta.xml").decode("utf-8")

    for label, xml_text in (("imsmanifest.xml", manifest_xml), ("module_meta.xml", module_xml)):
        try:
            ET.fromstring(xml_text)
        except ET.ParseError as e:
            errors.append("%s not well-formed: %s" % (label, e))

    if not errors:
        mroot = ET.fromstring(manifest_xml)
        cp = "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1"
        cc = "http://canvas.instructure.com/xsd/cccv1p0"
        res_ids = [r.get("identifier") for r in mroot.iter("{%s}resource" % cp)]
        dup_res = sorted(k for k, v in collections.Counter(res_ids).items() if v > 1)
        if dup_res:
            errors.append("duplicate resource identifiers: %s" % dup_res)
        item_ids = [i.get("identifier") for i in mroot.iter("{%s}item" % cp)]
        dup_items = sorted(k for k, v in collections.Counter(item_ids).items() if v > 1)
        if dup_items:
            errors.append("duplicate manifest item identifiers: %s" % dup_items)
        res_id_set = set(res_ids)
        file_hrefs = {f.get("href") for f in mroot.iter("{%s}file" % cp)}
        refs = {it.get("identifierref") for it in mroot.iter("{%s}item" % cp) if it.get("identifierref")}
        mroot2 = ET.fromstring(module_xml)
        meta_refs = {e.text for e in mroot2.iter("{%s}identifierref" % cc) if e.text}
        for ref in sorted(refs | meta_refs):
            if ref not in res_id_set:
                errors.append("dangling identifierref: %s" % ref)
        for href in sorted(file_hrefs):
            if href not in names:
                errors.append("missing file in zip: %s" % href)
        print("  resources: %d, files: %d, audio bundled: %d" % (
            len(res_id_set), len(file_hrefs), len([n for n in names if n.startswith("web_resources/")])))
    return errors


# ---- templates ----

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{manifest_id}" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd">
  <metadata>
    <schema>IMS Common Cartridge</schema>
    <schemaversion>1.1.0</schemaversion>
    <lomimscc:lom>
      <lomimscc:general>
        <lomimscc:title>
          <lomimscc:string>{course_title}</lomimscc:string>
        </lomimscc:title>
      </lomimscc:general>
      <lomimscc:lifeCycle>
        <lomimscc:contribute>
          <lomimscc:date>
            <lomimscc:dateTime>2026-08-16</lomimscc:dateTime>
          </lomimscc:date>
        </lomimscc:contribute>
      </lomimscc:lifeCycle>
      <lomimscc:rights>
        <lomimscc:copyrightAndOtherRestrictions>
          <lomimscc:value>yes</lomimscc:value>
        </lomimscc:copyrightAndOtherRestrictions>
        <lomimscc:description>
          <lomimscc:string>CC Attribution - http://creativecommons.org/licenses/by/4.0</lomimscc:string>
        </lomimscc:description>
      </lomimscc:rights>
    </lomimscc:lom>
  </metadata>
  <organizations default="org_1">
    <organization identifier="org_1" structure="rooted-hierarchy">
      <item identifier="LearningModules">
{org_items}
      </item>
    </organization>
  </organizations>
  <resources>
{resources}
  </resources>
</manifest>
"""

MODULE_META = """<?xml version="1.0" encoding="UTF-8"?>
<modules xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 http://canvas.instructure.com/xsd/cccv1p0.xsd">
{modules}
</modules>
"""

COURSE_SETTINGS = """<?xml version="1.0" encoding="UTF-8"?>
<course identifier="%s" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 http://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>%s</title>
  <course_code>%s</course_code>
  <default_view>modules</default_view>
  <license>cc_by</license>
  <default_wiki_editing_roles>teachers</default_wiki_editing_roles>
  <allow_student_wiki_edits>false</allow_student_wiki_edits>
</course>
""" % (COURSE_ID, esc(cd.COURSE["title"]), esc(cd.COURSE["code"]))

FILES_META = """<?xml version="1.0" encoding="UTF-8"?>
<fileMeta xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 http://canvas.instructure.com/xsd/cccv1p0.xsd">
</fileMeta>
"""

CANVAS_EXPORT_TXT = (
    "Q: What did the panda say when he was forced out of his natural habitat?\n"
    "A: This is un-BEAR-able\n"
)

RES_SYLLABUS = """    <resource identifier="res_syllabus" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="course_settings/syllabus.html" intendeduse="syllabus">
      <file href="course_settings/syllabus.html"/>
    </resource>"""

RES_CANVAS_EXPORT = """    <resource identifier="res_course_settings" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="course_settings/canvas_export.txt">
      <file href="course_settings/course_settings.xml"/>
      <file href="course_settings/module_meta.xml"/>
      <file href="course_settings/files_meta.xml"/>
      <file href="course_settings/canvas_export.txt"/>
    </resource>"""

WIKI_PAGE = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>{title}</title>
<meta name="identifier" content="{rid}"/>
<meta name="editing_roles" content="teachers"/>
<meta name="workflow_state" content="active"/>
</head>
<body>
<style>{styles}</style>
{body}
</body></html>
"""

ASSIGNMENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<assignment identifier="{rid}" xmlns="http://www.imsglobal.org/xsd/imscc_extensions/assignment" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imscc_extensions/assignment http://www.imsglobal.org/profile/cc/cc_extensions/cc_extresource_assignmentv1p0_v1p0.xsd">
  <title>{title}</title>
  <text texttype="text/html">{content}</text>
  <gradable points_possible="{points}">true</gradable>
  <submission_formats>
    <format type="file"/>
    <format type="url"/>
    <format type="text"/>
  </submission_formats>
</assignment>
"""


if __name__ == "__main__":
    if not os.path.isdir(PAGES_DIR):
        print("ERROR: theme folder not found: %s" % PAGES_DIR)
        sys.exit(1)
    out, resolved, audio_files = build()
    flat = [it for _m, its in resolved for it in its]
    n_wiki = sum(1 for k, *_ in flat if k == "wiki")
    n_asg = sum(1 for k, *_ in flat if k == "assignment")
    print("Built %s" % out)
    print("  modules: %d, items: %d (wiki %d, assignments %d), audio bundled: %d"
          % (len(cd.MODULES), len(flat), n_wiki, n_asg, len(audio_files)))
    errors = validate(out)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    print("Validation passed: XML well-formed, all references resolve.")
