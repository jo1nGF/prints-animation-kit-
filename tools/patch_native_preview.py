from pathlib import Path

source = Path("decompiled/Animation Kit.decompiled.jsx")
out_dir = Path("native-package")
out_dir.mkdir(exist_ok=True)
s = source.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit("Patch anchor not found: " + label)
    s = s.replace(old, new, 1)

# Replace the Flash-only preview with preset metadata and an actual AE preview comp.
a = s.index("function previewCore(number) {")
b = s.index("function executeCoreScript()", a)
s = s[:a] + r'''function previewCore(number) {
var n = Math.round(Number(number));
if (!previewInfo) { return; }
if (!n || n < 1 || n > loadedPresets || !textLines[n - 1]) {
previewInfo.text = "NATIVE PREVIEW\nSelect a preset to inspect its settings.";
return;
}
var parts = textLines[n - 1].split("!@ANIOM-PRESET@!");
var head = (parts[0] || "").split("^");
var properties = (parts[1] || "").split("#");
var names = [];
for (var p = 0; p < properties.length; p += 1) {
if (properties[p]) { names.push(properties[p].split(":")[0]); }
}
previewInfo.text = "PRESET " + n + " / " + loadedPresets + "\n" +
(head[0] || "2D") + "  |  " + (head[1] || "Range") + "  |  " +
((head[2] || "Characters").split(",")[0]) + "\n" +
(names.length ? names.join("  •  ") : "No animated properties") +
"\nUse PREVIEW IN COMP to inspect the real AE animation.";
}
function createNativePreview() {
try {
if (!app.project) { throw new Error("Open or create an After Effects project first."); }
var sourceComp = app.project.activeItem;
var w = (sourceComp && sourceComp instanceof CompItem) ? sourceComp.width : 1920;
var h = (sourceComp && sourceComp instanceof CompItem) ? sourceComp.height : 1080;
var rate = (sourceComp && sourceComp instanceof CompItem) ? sourceComp.frameRate : 30;
var previewComp = app.project.items.addComp("Animation Kit - Native Preview", w, h, 1, 5, rate);
var previewLayer = previewComp.layers.addText("ANIMATION KIT\nNative Preview");
previewLayer.name = "AK Preview Text";
previewLayer.inPoint = 0;
previewLayer.outPoint = 5;
try {
var textDocProp = previewLayer.property("ADBE Text Properties").property("ADBE Text Document");
var textDoc = textDocProp.value;
textDoc.fontSize = Math.min(120, Math.round(w / 12));
textDoc.fillColor = [1, 1, 1];
textDoc.applyFill = true;
textDoc.applyStroke = false;
textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
textDocProp.setValue(textDoc);
previewLayer.property("ADBE Transform Group").property("ADBE Position").setValue([w / 2, h / 2]);
} catch (styleError) {}
previewComp.openInViewer();
previewLayer.selected = true;
var previewApplied = executeCoreScript(previewLayer, true);
if (!previewApplied) { previewComp.remove(); return; }
previewComp.time = 0;
previewComp.openInViewer();
alert("Native preview composition created. Press Spacebar in the composition viewer to play the IN/OUT animation.");
} catch (previewError) {
alert("Could not create native preview: " + previewError.toString());
}
}
''' + s[b:]

replace_once(
    'function executeCoreScript() {\napp.beginUndoGroup("Animation Kit - Applying Preset");\ntry {',
    'function executeCoreScript(targetLayer, isPreview) {\napp.beginUndoGroup(isPreview ? "Animation Kit - Native Preview" : "Animation Kit - Applying Preset");\ntry {',
    "executeCoreScript signature"
)
replace_once(
    'for (var i = 1; i <= layerMarkers.numKeys; i += 1) { \nif ((layerMarkers.keyValue(i).comment == effect_in_out) && (layerMarkers.keyValue(i).cuePointName == marker_cuePointName)) {',
    'for (var i = layerMarkers.numKeys; i >= 1; i -= 1) { \nif ((layerMarkers.keyValue(i).comment == effect_in_out) && (layerMarkers.keyValue(i).cuePointName == marker_cuePointName)) {',
    "reverse marker iteration"
)
replace_once(
    'if (mainVar == "3D") { \ncurrentLayer.threeDPerChar = true;\n}',
    'currentLayer.threeDPerChar = (mainVar == "3D");',
    "2D/3D per-character state"
)
replace_once(
'''var appComp = app.project.activeItem;
if (!appComp) { 
alert("Please select composition!");
exit;
}
var currentLayer = appComp.selectedLayers[0];
if (!currentLayer.Text) { 
alert("Please select Text layer!");
exit;
}
if (((!parseInt(inSliderText.text)) || (!inSliderText.text.length)) || (inSliderText.text > loadedPresets)) { 
alert("Invalid number of preset [IN]");
exit;
}
if (((!parseInt(outSliderText.text)) || (!outSliderText.text.length)) || (outSliderText.text > loadedPresets)) { 
alert("Invalid number of preset [OUT]");
exit;
}''',
'''var appComp = app.project.activeItem;
var currentLayer = targetLayer || (appComp && appComp instanceof CompItem ? appComp.selectedLayers[0] : null);
if (!currentLayer) { throw new Error("Select a composition and a text layer first."); }
if (!currentLayer.property("ADBE Text Properties")) { throw new Error("The selected layer is not a text layer."); }
if (inCheckbox.value && (!/^\\d+$/.test(inSliderText.text) || Number(inSliderText.text) < 1 || Number(inSliderText.text) > loadedPresets)) {
throw new Error("Invalid IN preset number.");
}
if (outCheckbox.value && (!/^\\d+$/.test(outSliderText.text) || Number(outSliderText.text) < 1 || Number(outSliderText.text) > loadedPresets)) {
throw new Error("Invalid OUT preset number.");
}''',
    "target layer and input validation"
)
replace_once(
'''currentLayer.Text.property("Source Text").selected = true;
if (currentLayer.Text.property("Source Text").selected) {''',
'''if (!isPreview) {
currentLayer.Text.property("Source Text").selected = true;
}
if (!isPreview && currentLayer.Text.property("Source Text").selected) {''',
    "skip modified-property reveal in preview"
)
replace_once(
''' } catch (ex) {print(ex);
}
app.endUndoGroup();
}'''.lstrip(),
''' } catch (ex) {
alert("Animation Kit: " + ex.toString());
app.endUndoGroup();
return false;
}
app.endUndoGroup();
return true;
}'''.lstrip(),
    "error handling"
)
# Close the preset files after reading them.
s = s.replace(
'''while (!filePreset.eof) {
textLines[textLines.length] = filePreset.readln();
}
loadedPresets''',
'''while (!filePreset.eof) {
textLines[textLines.length] = filePreset.readln();
}
filePreset.close();
loadedPresets'''
)
# Replace the old SWF UI block.
replace_once(
'''var grpPreview = previewWinScr.add("group", undefined, "");
var preview = grpPreview.add("group", [0, 0, 240, 130], "");
if (availableFlashPlayer) { 
var flashPlayer = preview.add("FlashPlayer");
flashPlayer.size = [240, 130];
flashPlayer.loadMovie(loadPreviewFile_SWF());
}
else {
preview.add("image", [0, 0, 240, 130], iconPath + "naiSWF_image.png");
}''',
'''var grpPreview = previewWinScr.add("panel", [0, 0, 240, 130], "NATIVE PREVIEW");
grpPreview.orientation = "column";
grpPreview.alignChildren = ["fill", "fill"];
var previewInfo = grpPreview.add("statictext", undefined, "NATIVE PREVIEW\\\\nSelect a preset to inspect its settings.", {multiline: true});
previewInfo.alignment = ["fill", "fill"];
previewInfo.justify = "center";
var previewButton = grpPreview.add("button", undefined, "PREVIEW IN COMP");
previewButton.helpTip = "Create a temporary composition using the selected IN and OUT presets.";''',
    "native preview UI"
)
replace_once(
    'buttonExe.onClick = executeCoreScript;',
    'buttonExe.onClick = function () { executeCoreScript(null, false); };\npreviewButton.onClick = createNativePreview;',
    "wire native preview controls"
)
# The SWF helper is no longer needed.
if "function loadPreviewFile_SWF() {" in s:
    a = s.index("function loadPreviewFile_SWF() {")
    b = s.index("function setPreviewCore_point()", a)
    s = s[:a] + s[b:]
if "function setPreviewCore_point() {" in s:
    a = s.index("function setPreviewCore_point() {")
    b = s.index("function previewCore(number) {", a)
    s = s[:a] + s[b:]
s = s.replace('var previewTypeFile = ".swf";\nvar previewName = "PreviewPlayer";\n', "")
s = s.replace(
'''var availableFlashPlayer = true;
if (parseFloat(app.version) < 10) { 
availableFlashPlayer = false;
}''',
'''var availableFlashPlayer = false; // Flash Player is intentionally disabled in modern After Effects.
'''
)
# Keep the package independent from the original SWF.
if "FlashPlayer" in s or "loadMovie(" in s or "PreviewPlayer" in s:
    raise SystemExit("Flash dependency remains after native preview patch.")

out = out_dir / "Animation Kit 2026.jsx"
out.write_text(s, encoding="utf-8")
print("Created", out, "bytes:", out.stat().st_size)
