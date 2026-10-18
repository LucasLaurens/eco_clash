extends TestCase
## The documentation follows the code (CONTRIBUTING.md): every fighter is documented, every relative link
## resolves, and no term borrowed from another franchise appears anywhere in the project's text.

const FIGHTER_PAGES: Array[String] = ["res://README.md", "res://docs/fonctionnel/03-personnages.md"]
const LINKED_FILES: Array[String] = ["res://README.md", "res://PRODUCT.md"]
const SCANNED_FILES: Array[String] = ["res://README.md", "res://PRODUCT.md", "res://project.godot"]
## Folder -> extension of the text files to scan inside it.
const SCANNED_TREES := {
	"res://docs": ".md",
	"res://src": ".gd",
	"res://tests": ".gd",
	"res://data": ".tres",
	"res://scenes": ".tscn",
	"res://tools/assets": ".py",
}
## This file names the banned terms on purpose (CONTRIBUTING.md is not scanned for the same reason).
const SELF_PATH := "res://tests/unit/test_docs.gd"
const WORD_START := "(?<![\\p{L}\\p{N}_])"
const WORD_END := "(?![\\p{L}\\p{N}_])"
const BANNED_TERMS := "jak|daxter|precursor|précurseur|metal ?heads?|krimzon|ottsel|samos|sig|krew|spargus|haven"
## "Eco" survives only in the title (Eco Clash); identifiers like EcoPixel or eco_pixel never match a whole word.
const BANNED_ENERGY := "(?:éco|eco)(?!\\s+clash)"
const LINK_PATTERN := "\\]\\(([^)#\\s]+)(?:#[^)]*)?\\)"


func test_every_fighter_is_documented() -> void:
	# Arrange
	var pages := {}
	for path in FIGHTER_PAGES:
		pages[path] = FileAccess.get_file_as_string(path).to_lower()
	# Act & Assert
	for definition in FighterRoster.list_all():
		for path: String in pages:
			assert_true(String(pages[path]).contains(definition.display_name.to_lower()), "%s missing from %s" % [definition.display_name, path])


func test_every_relative_link_resolves() -> void:
	# Arrange
	var link := RegEx.create_from_string(LINK_PATTERN)
	var files := LINKED_FILES.duplicate()
	files.append_array(_list_files("res://docs", ".md"))
	# Act & Assert
	for path: String in files:
		for found in link.search_all(FileAccess.get_file_as_string(path)):
			var target := found.get_string(1)
			if target.begins_with("http"):
				continue
			var resolved := (path.get_base_dir() + "/" + target).simplify_path()
			assert_true(FileAccess.file_exists(resolved) or DirAccess.dir_exists_absolute(resolved), "%s links to missing %s" % [path, target])


func test_no_franchise_term_anywhere() -> void:
	# Arrange
	# Godot's RegEx does not fold accented capitals ("ÉCO"), so the text is lowered instead of using (?i).
	var banned := RegEx.create_from_string(WORD_START + "(?:" + BANNED_TERMS + "|" + BANNED_ENERGY + ")" + WORD_END)
	var files := SCANNED_FILES.duplicate()
	for root: String in SCANNED_TREES:
		files.append_array(_list_files(root, SCANNED_TREES[root]))
	files.erase(SELF_PATH)
	# Act & Assert
	assert_true(files.size() > 50, "scanned %d files" % files.size())
	for path: String in files:
		for found in banned.search_all(FileAccess.get_file_as_string(path).to_lower()):
			assert_true(false, "'%s' in %s" % [found.get_string(), path])


## O(n) over the files under root, recursive.
func _list_files(root: String, extension: String) -> Array[String]:
	var files: Array[String] = []
	for file_name in DirAccess.get_files_at(root):
		if file_name.ends_with(extension):
			files.append(root.path_join(file_name))
	for directory in DirAccess.get_directories_at(root):
		files.append_array(_list_files(root.path_join(directory), extension))
	return files
