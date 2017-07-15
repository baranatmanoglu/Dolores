<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Finie" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="finie" src="finie/finie.dlg" />
    </Dialogs>
    <Resources>
        <File name="finie" src="finie.py" />
        <File name="finie_settings" src="finie_settings.py" />
        <File name="index" src="html/index.html" />
        <File name="finie" src="html/js/finie.js" />
        <File name="loader" src="html/js/loader.js" />
        <File name="main" src="main.py" />
        <File name="jquery-2.1.4.min" src="html/js/jquery-2.1.4.min.js" />
        <File name="qimessaging_helper" src="html/js/qimessaging_helper.js" />
        <File name="pepper" src="html/css/pepper.css" />
        <File name="logo" src="html/img/logo.png" />
        <File name="pepper" src="html/img/pepper.png" />
        <File name="customerquery" src="customerquery.py" />
        <File name="creditoffer" src="html/img/creditoffer.jpg" />
    </Resources>
    <Topics>
        <Topic name="finie_enu" src="finie/finie_enu.top" topicName="finie" language="en_US" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
