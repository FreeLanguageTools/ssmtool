from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from .tools import *
from .dictionary import *
from .dictmanager import *

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.settings = parent.settings
        self.parent = parent
        self.setWindowTitle("Configure SSM")
        self.initWidgets()
        self.initTabs()
        self.setupWidgets()
        self.loadSettings()
        self.setupAutosave()

    def initWidgets(self):
        self.allow_editing = QCheckBox("Allow directly editing of text fields")
        self.lemmatization = QCheckBox("Use lemmatization (Requires restart to take effect)")
        self.lemmatization.setToolTip("Lemmatization means to get the original form of words."
            + "\nFor example, 'books' will be converted to 'book' during lookup if this option is set.")
        self.lemfreq = QCheckBox("Lemmatize before looking up frequency")
        self.lemfreq.setToolTip("Lemmatize words before trying to find them in the frequency list."
            + "\nUse this for frequency lists displayed on FLT.org, but do not use it "
            + "\nfor frequency lists from Migaku. ")
        self.target_language = QComboBox()
        self.deck_name = QComboBox()
        self.tags = QLineEdit()
        self.dict_source = QComboBox()
        self.dict_source2 = QComboBox()
        self.freq_source = QComboBox()
        self.gtrans_lang = QComboBox()
        self.note_type = QComboBox()
        self.sentence_field = QComboBox()
        self.word_field = QComboBox()
        self.definition_field = QComboBox()
        self.definition2_field = QComboBox()
        self.pronunciation_field = QComboBox()
        self.forvo = QCheckBox("Play Forvo pronunciation upon word selection")

        self.orientation = QComboBox()
        self.text_scale = QSlider(Qt.Horizontal)

        self.text_scale.setTickPosition(QSlider.TicksBelow)
        self.text_scale.setTickInterval(10)
        self.text_scale.setSingleStep(5)
        self.text_scale.setValue(100)
        self.text_scale.setMinimum(50)
        self.text_scale.setMaximum(250)
        self.text_scale_label = QLabel("1.00x")        
        self.text_scale_box = QWidget()
        self.text_scale_box_layout = QHBoxLayout()
        self.text_scale_box.setLayout(self.text_scale_box_layout)
        self.text_scale_box_layout.addWidget(self.text_scale)
        self.text_scale_box_layout.addWidget(self.text_scale_label)

        self.orientation.addItems([
            "Vertical", 
            "Horizontal", 
            ])

        self.anki_api = QLineEdit()
        self.about_sa = QScrollArea()
        self.host = QLineEdit()
        self.port = QSpinBox()
        self.port.setMinimum(1024)
        self.port.setMaximum(49151)
        self.importdict = QPushButton('Manage local dictionaries..')

        self.about = QLabel(
            '''
© 2021 FreeLanguageTools<br><br>
Visit <a href="https://freelanguagetools.org">FreeLanguageTools.org</a> for more info on how to use this tool.<br>
You can also talk to us on <a href="https://webchat.kde.org/#/room/#flt:midov.pl">Matrix</a>
or <a href="https://t.me/fltchat">Telegram</a> for support.<br><br>

Simple Sentence Mining (SSM, ssmtool) is free software available under the terms of
<a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GNU GPLv3</a>.<br><br>
If you found a bug, or have enhancement ideas, 
feel free to open an issue on the 
Github <a href=https://github.com/FreeLanguageTools/ssmtool>repository</a>.<br><br>


This program is yours to keep. There is no EULA you need to agree to.
No data is sent to any server other than the configured dictionary APIs.
Statistics data are stored locally.
<br><br>
Credits: <br><a href="https://en.wiktionary.org/wiki/Wiktionary:Main_Page">Wiktionary API</a><br>
If you find this tool useful, you can donate to these projects.
            '''
        )
        self.about.setTextFormat(Qt.RichText)
        self.about.setOpenExternalLinks(True)
        self.about_sa.setWidget(self.about)
        self.about.setWordWrap(True)
        self.about.adjustSize()
        self.importdict.clicked.connect(self.dictmanager)

    def dictmanager(self):
        importer = DictManager(self)
        importer.exec()
    
    def initTabs(self):
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab1.layout = QFormLayout(self.tab1)
        self.tab2 = QWidget()
        self.tab2.layout = QFormLayout(self.tab2)
        self.tab3 = QWidget()
        self.tab3.layout = QFormLayout(self.tab3)
        self.tab4 = QWidget()
        self.tab4.layout = QFormLayout(self.tab4)
        self.tab5 = QWidget()
        self.tab5.layout = QVBoxLayout(self.tab5)

        self.tabs.resize(250, 300)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)

        self.tabs.addTab(self.tab1, "Dictionary")
        self.tabs.addTab(self.tab2, "Anki")
        self.tabs.addTab(self.tab3, "API")
        self.tabs.addTab(self.tab4, "Interface")
        self.tabs.addTab(self.tab5, "About")

    def setupWidgets(self):
        self.target_language.addItems(code.keys())
        self.gtrans_lang.addItems(code.keys())
        
        self.tab1.layout.addRow(self.lemmatization)
        self.tab1.layout.addRow(self.lemfreq)
        self.tab1.layout.addRow(self.forvo)
        self.tab1.layout.addRow(QLabel("Target language"), self.target_language)
        self.tab1.layout.addRow(QLabel("Dictionary source 1"), self.dict_source)
        self.tab1.layout.addRow(QLabel("Dictionary source 2"), self.dict_source2)
        self.tab1.layout.addRow(QLabel("Frequency list"), self.freq_source)
        self.tab1.layout.addRow(QLabel("Google translate: To"), self.gtrans_lang)
        self.tab1.layout.addRow(self.importdict)


        self.tab2.layout.addRow(QLabel('AnkiConnect API'), self.anki_api)
        self.tab2.layout.addRow(QLabel("Deck name"), self.deck_name)
        self.tab2.layout.addRow(QLabel('Default tags'), self.tags)
        self.tab2.layout.addRow(QLabel("Note type"), self.note_type)
        self.tab2.layout.addRow(QLabel('Field name for "Sentence"'), self.sentence_field)
        self.tab2.layout.addRow(QLabel('Field name for "Word"'), self.word_field)
        self.tab2.layout.addRow(QLabel('Field name for "Definition"'), self.definition_field)
        self.tab2.layout.addRow(QLabel('Field name for "Definition#2"'), self.definition2_field)
        self.tab2.layout.addRow(QLabel('Field name for "Pronunciation"'), self.pronunciation_field)

        self.tab3.layout.addRow(QLabel('<i>Most users should not need to change these settings.</i>'))
        self.tab3.layout.addRow(QLabel("API host"), self.host)
        self.tab3.layout.addRow(QLabel("API port"), self.port)

        self.tab4.layout.addRow(QLabel("<b>All settings on this tab requires restart to take effect.</b>"))
        self.tab4.layout.addRow(self.allow_editing)
        self.tab4.layout.addRow(QLabel("Interface layout"), self.orientation)
        self.tab4.layout.addRow(QLabel("Text scale"), self.text_scale_box)

        self.tab5.layout.addWidget(self.about_sa)
        
        self.text_scale.valueChanged.connect(
            lambda _: self.text_scale_label.setText(format(self.text_scale.value()/100, "1.2f") + "x")
            )

        
    def setupAutosave(self):
        self.allow_editing.clicked.connect(self.syncSettings)
        self.lemmatization.clicked.connect(self.syncSettings)
        self.lemfreq.clicked.connect(self.syncSettings)
        self.forvo.clicked.connect(self.syncSettings)
        self.freq_source.currentTextChanged.connect(self.syncSettings)
        self.dict_source.currentTextChanged.connect(self.syncSettings)
        self.dict_source.currentTextChanged.connect(self.loadDict2Options)
        self.dict_source2.currentTextChanged.connect(self.syncSettings)
        self.dict_source2.currentTextChanged.connect(self.warnRestart)
        self.target_language.currentTextChanged.connect(self.loadDictionaries)
        self.target_language.currentTextChanged.connect(self.syncSettings)
        self.gtrans_lang.currentTextChanged.connect(self.syncSettings)
        self.deck_name.currentTextChanged.connect(self.syncSettings)
        self.tags.editingFinished.connect(self.syncSettings)
        self.note_type.currentTextChanged.connect(self.syncSettings)
        self.note_type.currentTextChanged.connect(self.loadFields)
        self.sentence_field.currentTextChanged.connect(self.syncSettings)
        self.sentence_field.currentTextChanged.connect(self.checkCorrectness)
        self.word_field.currentTextChanged.connect(self.syncSettings)
        self.word_field.currentTextChanged.connect(self.checkCorrectness)
        self.definition_field.currentTextChanged.connect(self.syncSettings)
        self.definition_field.currentTextChanged.connect(self.checkCorrectness)
        self.definition2_field.currentTextChanged.connect(self.syncSettings)
        self.definition2_field.currentTextChanged.connect(self.checkCorrectness)
        self.pronunciation_field.currentTextChanged.connect(self.syncSettings)
        self.pronunciation_field.currentTextChanged.connect(self.checkCorrectness)
        self.anki_api.editingFinished.connect(self.syncSettings)
        self.anki_api.editingFinished.connect(self.loadSettings)
        self.host.textChanged.connect(self.syncSettings)
        self.port.valueChanged.connect(self.syncSettings)
        self.text_scale.valueChanged.connect(self.syncSettings)
        self.orientation.currentTextChanged.connect(self.syncSettings)

    def loadDictionaries(self):
        custom_dicts = self.settings.value("custom_dicts", [], type=list)
        self.dict_source.clear()
        dicts = getDictsForLang(code[self.target_language.currentText()], custom_dicts)
        self.dict_source.addItems(dicts)

    def loadDict2Options(self):
        custom_dicts = self.settings.value("custom_dicts", [], type=list)
        curtext = self.dict_source2.currentText()
        self.dict_source2.blockSignals(True)
        self.dict_source2.clear()
        dicts = getDictsForLang(code[self.target_language.currentText()], custom_dicts)
        self.dict_source2.addItem("Disabled")
        for item in dicts:
            if self.dict_source.currentText() != item:
                self.dict_source2.addItem(item)
        # Keep current choice if available
        if self.dict_source2.findText(curtext) != -1:
            self.dict_source2.setCurrentText(curtext)
        self.dict_source2.blockSignals(False)

    def loadFreqSources(self):
        custom_dicts = self.settings.value("custom_dicts", [], type=list)
        sources = getFreqlistsForLang(code[self.target_language.currentText()], custom_dicts)
        self.freq_source.clear()
        self.freq_source.addItem("Disabled")
        for item in sources:
            self.freq_source.addItem(item)


    def loadSettings(self):
        self.forvo.setChecked(self.settings.value("forvo", False, type=bool))
        self.allow_editing.setChecked(self.settings.value("allow_editing", True, type=bool))
        self.lemmatization.setChecked(self.settings.value("lemmatization", True, type=bool))
        self.lemfreq.setChecked(self.settings.value("lemfreq", False, type=bool))
        self.orientation.setCurrentText(self.settings.value("orientation", "Vertical"))
        self.text_scale.setValue(self.settings.value("text_scale", 100, type=int))
        self.target_language.setCurrentText(self.settings.value("target_language"))
        self.loadDictionaries()
        self.dict_source.setCurrentText(self.settings.value("dict_source", "Wiktionary (English)"))
        self.loadDict2Options()
        self.dict_source2.setCurrentText(self.settings.value("dict_source2", "Wiktionary (English)"))
        self.loadFreqSources()
        self.freq_source.setCurrentText(self.settings.value("freq_source", "Disabled"))
        self.gtrans_lang.setCurrentText(self.settings.value("gtrans_lang", "English"))
        self.anki_api.setText(self.settings.value("anki_api", "http://localhost:8765"))
        self.tags.setText(self.settings.value("tags", "ssmtool"))
        api = self.anki_api.text()

        self.host.setText(self.settings.value("host", "127.0.0.1"))
        self.port.setValue(self.settings.value("port", 39284, type=int))

        try:
            _ = getVersion(api)
        except Exception as e:
            self.errorNoConnection(e)
            return

        decks = getDeckList(api)
        self.deck_name.clear()
        self.deck_name.addItems(decks)
        self.deck_name.setCurrentText(self.settings.value("deck_name"))

        note_types = getNoteTypes(api)
        self.note_type.clear()
        self.note_type.addItems(note_types)
        self.note_type.setCurrentText(self.settings.value("note_type"))
        self.loadFields()

    def loadFields(self):
        api = self.anki_api.text()
        try:
            _ = getVersion(api)
        except Exception as e:
            self.errorNoConnection(e)
            return
        current_type = self.note_type.currentText()


        if current_type == "":
            return

        fields = getFields(api, current_type)
        if "Disabled" in fields:
            self.warn("You must not have a field named 'Disabled'. You *will* encounter bugs.")
        # Temporary store fields 
        sent = self.sentence_field.currentText()
        word = self.word_field.currentText()
        def1 = self.definition_field.currentText()
        def2 = self.definition2_field.currentText()
        pron = self.pronunciation_field.currentText()

        # Block signals temporarily to avoid warning dialogs
        self.sentence_field.blockSignals(True)
        self.word_field.blockSignals(True)
        self.definition_field.blockSignals(True)
        self.definition2_field.blockSignals(True)
        self.pronunciation_field.blockSignals(True)

        self.sentence_field.clear()
        self.sentence_field.addItems(fields)

        self.word_field.clear()
        self.word_field.addItems(fields)

        self.definition_field.clear()
        self.definition_field.addItems(fields)

        self.definition2_field.clear()
        self.definition2_field.addItem("Disabled")
        self.definition2_field.addItems(fields)     

        self.pronunciation_field.clear()
        self.pronunciation_field.addItem("Disabled")
        self.pronunciation_field.addItems(fields)   

        self.sentence_field.setCurrentText(self.settings.value("sentence_field"))
        self.word_field.setCurrentText(self.settings.value("word_field"))
        self.definition_field.setCurrentText(self.settings.value("definition_field"))
        self.pronunciation_field.setCurrentText(self.settings.value("pronunciation_field"))

        if self.sentence_field.findText(sent) != -1:
            self.sentence_field.setCurrentText(sent)
        if self.word_field.findText(word) != -1:
            self.word_field.setCurrentText(word)
        if self.definition_field.findText(def1) != -1:
            self.definition_field.setCurrentText(def1)
        if self.definition2_field.findText(def2) != -1:
            self.definition2_field.setCurrentText(def2)
        if self.pronunciation_field.findText(def2) != -1:
            self.pronunciation_field.setCurrentText(def2)
        
        self.sentence_field.blockSignals(False)
        self.word_field.blockSignals(False)
        self.definition_field.blockSignals(False)
        self.definition2_field.blockSignals(False)
        self.pronunciation_field.blockSignals(False)

    def syncSettings(self):
        self.settings.setValue("forvo", self.forvo.isChecked())
        self.settings.setValue("allow_editing", self.allow_editing.isChecked())
        self.settings.setValue("lemmatization", self.lemmatization.isChecked())
        self.settings.setValue("lemfreq", self.lemfreq.isChecked())
        self.settings.setValue("orientation", self.orientation.currentText())
        self.settings.setValue("target_language", self.target_language.currentText())
        self.settings.setValue("dict_source", self.dict_source.currentText())
        self.settings.setValue("dict_source2", self.dict_source2.currentText())
        self.settings.setValue("freq_source", self.freq_source.currentText())
        self.settings.setValue("gtrans_lang", self.gtrans_lang.currentText())
        self.settings.setValue("anki_api", self.anki_api.text())
        self.settings.setValue("host", self.host.text())
        self.settings.setValue("port", self.port.value())
        self.settings.setValue("text_scale", self.text_scale.value())
        try:
            api = self.anki_api.text()
            getVersion(api)
            self.settings.setValue("deck_name", self.deck_name.currentText())
            self.settings.setValue("note_type", self.note_type.currentText())
            self.settings.setValue("tags", self.tags.text())
            self.settings.setValue("sentence_field", self.sentence_field.currentText())
            self.settings.setValue("word_field", self.word_field.currentText())
            self.settings.setValue("definition_field", self.definition_field.currentText())
            self.settings.setValue("definition2_field", self.definition2_field.currentText())
            self.settings.setValue("pronunciation_field", self.pronunciation_field.currentText())
        except Exception as e:
            pass
        self.settings.sync()
    
    def errorNoConnection(self, error):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(str(error) + 
            "\nAnkiConnect must be running to use the configuration tool.")
        msg.exec()


    def warn(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        msg.exec()

    def warnRestart(self):
        if self.dict_source2.currentText() and self.dict_source2.currentText() != "Disabled":
            self.warn("You must restart for this tool to work properly after changing Dictionary source #2."
            + "\nIf you have just enabled it, you must also configure a definition 2 field in the Anki tab, or otherwise you will not be able to add notes.")
    
    def checkCorrectness(self):
        # No two fields should be the same
        set_fields = [self.sentence_field.currentText(), self.word_field.currentText(),
            self.definition_field.currentText(), self.definition2_field.currentText()]

        if len(set(set_fields)) != len(set_fields):
            self.warn("All fields must be set to different note fields.\nYou *will* encounter bugs.")