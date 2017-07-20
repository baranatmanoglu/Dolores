<?xml version="1.0" encoding="UTF-8" ?>
<Package name="QRReaderApp" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="barcode_detected" src="barcode_detected/barcode_detected.dlg" />
    </Dialogs>
    <Resources>
        <File name="index" src="html/index.html" />
        <File name="__init__" src="kairos_face/__init__.py" />
        <File name="__init__" src="kairos_face/__init__.pyc" />
        <File name="detect" src="kairos_face/detect.py" />
        <File name="detect" src="kairos_face/detect.pyc" />
        <File name="enroll" src="kairos_face/enroll.py" />
        <File name="enroll" src="kairos_face/enroll.pyc" />
        <File name="entities" src="kairos_face/entities.py" />
        <File name="entities" src="kairos_face/entities.pyc" />
        <File name="exceptions" src="kairos_face/exceptions.py" />
        <File name="exceptions" src="kairos_face/exceptions.pyc" />
        <File name="gallery" src="kairos_face/gallery.py" />
        <File name="gallery" src="kairos_face/gallery.pyc" />
        <File name="recognize" src="kairos_face/recognize.py" />
        <File name="recognize" src="kairos_face/recognize.pyc" />
        <File name="remove" src="kairos_face/remove.py" />
        <File name="remove" src="kairos_face/remove.pyc" />
        <File name="settings" src="kairos_face/settings.py" />
        <File name="settings" src="kairos_face/settings.pyc" />
        <File name="utils" src="kairos_face/utils.py" />
        <File name="utils" src="kairos_face/utils.pyc" />
        <File name="verify" src="kairos_face/verify.py" />
        <File name="verify" src="kairos_face/verify.pyc" />
        <File name="main" src="main.py" />
        <File name="customerquery" src="customerquery.py" />
        <File name="jquery-2.1.4.min" src="html/js/jquery-2.1.4.min.js" />
        <File name="main" src="html/js/main.js" />
        <File name="qimessaging_helper" src="html/js/qimessaging_helper.js" />
        <File name="videoutils" src="html/js/videoutils.js" />
        <File name="pepper" src="html/css/pepper.css" />
    </Resources>
    <Topics>
        <Topic name="barcode_detected_enu" src="barcode_detected/barcode_detected_enu.top" topicName="barcode_detected" language="en_US" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
