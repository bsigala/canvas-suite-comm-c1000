import zipfile
import os
import uuid

# Configuration
BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
ZIP_PATH = os.path.join(BASE_DIR, "COMM_C1000_Chapters_1-5_Quiz_QTI.zip")

# --------------------------------------------------------------------------------
# DATA STRUCTURES
# --------------------------------------------------------------------------------

class QuizQuestion:
    def __init__(self, qid, title, prompt, question_type, answers, correct_answer_index, points=2):
        self.id = qid
        self.title = title
        self.prompt = prompt
        self.question_type = question_type # 'multiple_choice_question', 'true_false_question'
        self.answers = answers # List of strings
        self.correct_answer_index = correct_answer_index
        self.points = points

    def get_full_text_html(self):
        # Elegant styled HTML panel for the Canvas quiz question presentation
        html = f"""
        <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 25px; background-color: #faf8f5; border: 1px solid #e6dfd5; border-left: 6px solid #c68a4c; border-radius: 12px; box-shadow: 0 4px 12px rgba(140, 94, 40, 0.03);">
            <div style="margin-bottom: 20px;">
                <span style="background-color: #c68a4c; color: #ffffff; font-size: 0.75rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 10px;">Public Speaking Challenge</span>
                <h3 style="color: #8c5e28; font-family: 'Georgia', serif; font-size: 1.3rem; font-weight: 600; margin: 0 0 10px 0; line-height: 1.3;">{self.title}</h3>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #2b2a27; margin: 0;">
                    {self.prompt}
                </p>
            </div>
            <div style="margin-top: 25px; padding-top: 15px; border-top: 1px dashed #e6dfd5; font-size: 0.8rem; color: #605e5a;">
                Rio Hondo College · COMM C1000 Intro to Public Speaking (formerly SPCH 101) · Mr. Benjamin Sigala
            </div>
        </div>
        """
        return html


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
        # Answers XML
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

# --------------------------------------------------------------------------------
# COMPILING THE QUESTIONS
# --------------------------------------------------------------------------------

questions_data = [
    QuizQuestion(
        qid="q001",
        title="OER Textbook core focus",
        prompt="According to our OER textbook, 'It's About Them: Public Speaking in the 21st Century,' what is the absolute core focus of public speaking?",
        question_type="multiple_choice_question",
        answers=[
            "Focusing entirely on the speaker's own delivery style and performance mechanics.",
            "Overcoming speech anxiety through absolute memorization of the script.",
            "Keeping your message fully audience-centric, designing and delivering it with your listeners' needs and reactions in mind.",
            "Using complex graphic slides to entertain the audience."
        ],
        correct_answer_index=2,
        points=2
    ),
    QuizQuestion(
        qid="q002",
        title="Student Learning Outcomes (SLOs)",
        prompt="According to our COMM C1000 syllabus, which of the following is NOT one of our three core Student Learning Outcomes (SLOs) assessed in oral presentations?",
        question_type="multiple_choice_question",
        answers=[
            "In an oral presentation, students will effectively implement appropriate content and research.",
            "In an oral presentation, students will display professional level multi-spectral remote sensing analysis.",
            "In an oral presentation, students will display effective speech delivery.",
            "In an oral presentation, students will effectively organize speech content."
        ],
        correct_answer_index=1,
        points=2
    ),
    QuizQuestion(
        qid="q003",
        title="Academic Integrity Conduct",
        prompt="Under the Rio Hondo Student Code of Conduct and Mr. Sigala's academic integrity policies, which of the following actions constitutes a direct violation?",
        question_type="multiple_choice_question",
        answers=[
            "Using our free OER digital textbook to draft your speech outlines.",
            "Citing your AI usage and ensuring it meets our course guidelines.",
            "Allowing another individual to assume your identity inside Canvas to complete your work or enhance your grade.",
            "Recording your check-in video on a smartphone and uploading an iCloud photo link."
        ],
        correct_answer_index=2,
        points=2
    ),
    QuizQuestion(
        qid="q004",
        title="Instructor Response Times",
        prompt="According to Mr. Benjamin Sigala's COMM C1000 Communication Policy, what is the maximum expected response window for messages received Monday through Thursday through the Canvas Inbox?",
        question_type="multiple_choice_question",
        answers=[
            "12 Hours",
            "24 Hours",
            "48 Hours",
            "72 Hours"
        ],
        correct_answer_index=2,
        points=2
    ),
    QuizQuestion(
        qid="q005",
        title="Speech Anxiety Nature",
        prompt="Speech anxiety (commonly called 'stage fright') is a completely natural psychological and physiological reaction that can be successfully mitigated through systematic, audience-centric preparation and regular delivery practice.",
        question_type="true_false_question",
        answers=[
            "True",
            "False"
        ],
        correct_answer_index=0,
        points=2
    )
]

# --------------------------------------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------------------------------------

def main():
    assessment_id = f"comm_c1000_chapter_1_5_quiz"
    manifest_xml = create_manifest_xml(assessment_id)
    assessment_xml = create_assessment_xml(assessment_id, "COMM C1000: Chapters 1-5 Quiz (OER & Syllabus)", questions_data)
    
    # Save files temporarily to create zip
    manifest_file = "imsmanifest.xml"
    assessment_file = f"{assessment_id}.xml"
    
    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write(manifest_xml)
    with open(assessment_file, "w", encoding="utf-8") as f:
        f.write(assessment_xml)
        
    # Zip package
    with zipfile.ZipFile(ZIP_PATH, 'w') as zipf:
        zipf.write(manifest_file)
        zipf.write(assessment_file)
        
    # Clean up local files
    os.remove(manifest_file)
    os.remove(assessment_file)
    
    print(f"SUCCESS: Programmatically compiled ready-to-import QTI Quiz Zip at:\n-> {ZIP_PATH}")

if __name__ == "__main__":
    main()
