#!/usr/bin/env python3
"""
COMM C1000 — Chapters 6-16 Quiz Bank (Canvas QTI)
===================================================
Completes the 16-chapter OER quiz coverage. The Chapters 1-5 zip already
exists (COMM_C1000_Chapters_1-5_Quiz_QTI.zip); this script emits the
matching Chapters 6-16 package with one mastery item per chapter.

Answer keys follow the master transcript:
  Ch. 11 (Using Language) -> A, Ch. 15 (Persuasive) -> C.
"""

import zipfile
import os
import uuid

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
ZIP_PATH = os.path.join(BASE_DIR, "COMM_C1000_Chapters_6-16_Quiz_QTI.zip")


class QuizQuestion:
    def __init__(self, qid, title, prompt, question_type, answers, correct_answer_index, points=2):
        self.id = qid
        self.title = title
        self.prompt = prompt
        self.question_type = question_type
        self.answers = answers
        self.correct_answer_index = correct_answer_index
        self.points = points

    def get_full_text_html(self):
        return f"""
        <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 25px; background-color: #faf8f5; border: 1px solid #e6dfd5; border-left: 6px solid #c68a4c; border-radius: 12px;">
            <div style="margin-bottom: 20px;">
                <span style="background-color: #c68a4c; color: #ffffff; font-size: 0.75rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 10px;">Public Speaking Challenge</span>
                <h3 style="color: #8c5e28; font-family: 'Georgia', serif; font-size: 1.3rem; font-weight: 600; margin: 0 0 10px 0; line-height: 1.3;">{self.title}</h3>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #2b2a27; margin: 0;">{self.prompt}</p>
            </div>
            <div style="margin-top: 25px; padding-top: 15px; border-top: 1px dashed #e6dfd5; font-size: 0.8rem; color: #605e5a;">
                Rio Hondo College · COMM C1000 Intro to Public Speaking (formerly SPCH 101) · Mr. Benjamin Sigala
            </div>
        </div>
        """


def create_manifest_xml(assessment_id):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="man_{uuid.uuid4().hex}" xmlns="http://www.imsglobal.org/xsd/imscp_v1p1" xmlns:lor="http://www.imsglobal.org/xsd/imsmd_v1p2" xmlns:adhoc="http://www.imsglobal.org/xsd/imsadhoc_v1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2.xsd">
  <metadata>
    <schema>IMS Content</schema>
    <schemaversion>1.1</schemaversion>
  </metadata>
  <organizations />
  <resources>
    <resource identifier="{assessment_id}" type="imsqti_xmlv1p2/imscc_xmlv1p1/assessment">
      <file href="{assessment_id}.xml"/>
    </resource>
  </resources>
</manifest>"""


def create_assessment_xml(assessment_id, quiz_title, questions):
    items_xml = ""
    for q in questions:
        response_labels = ""
        correct_ident = ""
        for i, ans in enumerate(q.answers):
            ans_ident = f"ans_{q.id}_{i}"
            if i == q.correct_answer_index:
                correct_ident = ans_ident
            response_labels += f"""
              <response_label ident="{ans_ident}">
                <material>
                  <mattext texttype="text/plain">{ans}</mattext>
                </material>
              </response_label>"""

        items_xml += f"""
      <item ident="{q.id}" title="{q.title}">
        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>question_type</fieldlabel>
              <fieldentry>{q.question_type}</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>points_possible</fieldlabel>
              <fieldentry>{q.points}.0</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
        <presentation>
          <material>
            <mattext texttype="text/html"><![CDATA[{q.get_full_text_html()}]]></mattext>
          </material>
          <response_lid ident="response1" rcardinality="Single">
            <render_choice>
              {response_labels}
            </render_choice>
          </response_lid>
        </presentation>
        <resprocessing>
          <outcomes>
            <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
          </outcomes>
          <respcondition continue="No">
            <conditionvar>
              <varequal respident="response1">{correct_ident}</varequal>
            </conditionvar>
            <setvar action="Set" varname="SCORE">100</setvar>
          </respcondition>
        </resprocessing>
      </item>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2.xsd">
  <assessment ident="{assessment_id}" title="{quiz_title}">
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>cc_maxattempts</fieldlabel>
        <fieldentry>1</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
    <section ident="root_section">
      {items_xml}
    </section>
  </assessment>
</questestinterop>"""


QUESTIONS = [
    QuizQuestion("q006", "Ch. 6: Selecting a Topic and Purpose",
        "When selecting a speech topic, which strategy best serves both the speaker and the audience?",
        "multiple_choice_question",
        [
            "Choose whatever topic requires the least preparation.",
            "Brainstorm from your own interests and expertise, then refine the topic to fit the audience's needs and the occasion.",
            "Wait for the instructor to assign a specific topic.",
            "Pick the broadest possible subject so there is plenty to talk about.",
        ], 1),
    QuizQuestion("q007", "Ch. 7: Researching Your Speech",
        "Which of the following is the strongest research practice for an informative or persuasive speech?",
        "multiple_choice_question",
        [
            "Rely on a single website that agrees with your argument.",
            "Cite only facts you happen to remember.",
            "Draw on a mix of peer-reviewed academic sources, books, and credible government or primary sources, evaluating each for currency and relevance.",
            "Avoid library databases because they are too time-consuming.",
        ], 2),
    QuizQuestion("q008", "Ch. 8: Supporting Materials",
        "What is the primary role of supporting materials (examples, statistics, testimony) in a speech?",
        "multiple_choice_question",
        [
            "To fill time so the speech meets the length requirement.",
            "To impress the audience with large numbers.",
            "To replace the need for a clear organizational structure.",
            "To clarify, prove, and add interest to the speaker's claims.",
        ], 3),
    QuizQuestion("q009", "Ch. 9: Organizing and Outlining",
        "According to standard outlining practice, a full-sentence preparation outline should:",
        "multiple_choice_question",
        [
            "Use only single keywords so it fits on one card.",
            "Be written in complete sentences with a consistent pattern of symbols and indentation.",
            "Be memorized word-for-word for delivery.",
            "Omit transitions since they are implied.",
        ], 1),
    QuizQuestion("q010", "Ch. 10: Introductions and Conclusions",
        "Which of the following belongs in an effective speech introduction?",
        "multiple_choice_question",
        [
            "A brand-new main point not covered in the body.",
            "The longest story you can tell, regardless of relevance.",
            "An attention getter, a credibility statement, a thesis, and a preview of main points.",
            "An apology for your lack of preparation.",
        ], 2),
    QuizQuestion("q011", "Ch. 11: Using Language",
        "Effective oral language in public speaking is best described as:",
        "multiple_choice_question",
        [
            "Concrete, vivid, and appropriate for the audience and occasion.",
            "Dense with technical jargon to demonstrate expertise.",
            "Abstract and intentionally vague to remain safe.",
            "Composed of long, complex sentences to sound formal.",
        ], 0),
    QuizQuestion("q012", "Ch. 12: Delivering Your Speech",
        "Extemporaneous delivery — the standard for COMM C1000 speeches — means:",
        "multiple_choice_question",
        [
            "Reading the speech word-for-word from a manuscript.",
            "Memorizing every word verbatim.",
            "Speaking from a keyword outline or cue cards while maintaining conversational eye contact with the audience.",
            "Improvising entirely with no preparation or notes.",
        ], 2),
    QuizQuestion("q013", "Ch. 13: Presentation Aids",
        "Which design principle best reduces cognitive load in a slide deck?",
        "multiple_choice_question",
        [
            "Including dense paragraphs so the audience can read along.",
            "Using high-contrast visuals with minimal text on each slide.",
            "Mixing many different fonts and bright colors.",
            "Reading the slides aloud word-for-word.",
        ], 1),
    QuizQuestion("q014", "Ch. 14: Informative Speaking",
        "The central goal of an informative speech is to:",
        "multiple_choice_question",
        [
            "Change the audience's deeply held beliefs.",
            "Teach the audience something new in a clear, objective, and engaging way.",
            "Sell a product or service.",
            "Win a formal debate.",
        ], 1),
    QuizQuestion("q015", "Ch. 15: Persuasive Speaking",
        "Monroe's Motivated Sequence arranges a persuasive speech in which order?",
        "multiple_choice_question",
        [
            "Need, Attention, Action, Satisfaction, Visualization.",
            "Attention, Visualization, Need, Action, Satisfaction.",
            "Attention, Need, Satisfaction, Visualization, Action.",
            "Action, Attention, Need, Satisfaction, Visualization.",
        ], 2),
    QuizQuestion("q016", "Ch. 16: Special Occasion Speaking",
        "A ceremonial or special-occasion speech (toast, tribute, or award presentation) should primarily:",
        "multiple_choice_question",
        [
            "Inform the audience with statistics and data.",
            "Persuade the audience to adopt a policy.",
            "Analyze another speaker's rhetoric.",
            "Honor the occasion and evoke fitting emotions through expressive language.",
        ], 3),
]


def main():
    assessment_id = "comm_c1000_chapter_6_16_quiz"
    manifest_xml = create_manifest_xml(assessment_id)
    assessment_xml = create_assessment_xml(
        assessment_id, "COMM C1000: Chapters 6-16 Quiz (OER Mastery)", QUESTIONS
    )

    manifest_file = "imsmanifest.xml"
    assessment_file = f"{assessment_id}.xml"
    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write(manifest_xml)
    with open(assessment_file, "w", encoding="utf-8") as f:
        f.write(assessment_xml)

    with zipfile.ZipFile(ZIP_PATH, "w") as zipf:
        zipf.write(manifest_file)
        zipf.write(assessment_file)

    os.remove(manifest_file)
    os.remove(assessment_file)

    print("SUCCESS: Chapters 6-16 QTI quiz compiled.")
    print(f"-> {ZIP_PATH}")
    print(f"   Items: {len(QUESTIONS)} (one per chapter, Ch. 6 through Ch. 16)")


if __name__ == "__main__":
    main()
