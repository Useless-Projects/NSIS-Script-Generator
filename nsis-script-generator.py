#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NSIS Script Generator 1.1.0
# © 2025 Thibault Savenkoff

import os
import sys
import datetime
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Helper Functions for User Input ---

def ask_string(prompt, default=None, allow_empty=False): # <--- Make sure allow_empty=False is HERE
    """Asks the user for a string input, providing an optional default."""
    prompt_text = f"{prompt}"
    if default is not None:
        prompt_text += f" [{default}]"
    prompt_text += ": "

    while True:
        try:
            user_input = input(prompt_text).strip()
            if user_input: # If user typed something, return it
                return user_input
            elif default is not None: # If user pressed Enter AND there is a default, return default
                return default
            elif allow_empty: # If user pressed Enter, there is NO default, BUT empty is allowed
                return "" # Return the empty string
            else: # If user pressed Enter, there is NO default, and empty is NOT allowed
                print("Input cannot be empty.")
        except EOFError:
            print("\nInput aborted.")
            print("\nBye!")
            sys.exit(1)
        except KeyboardInterrupt:
             print("\nOperation cancelled by user.")
             print("\nBye!")
             sys.exit(1)


def ask_path(prompt, default=None, check_exists=None, is_dir=False, allow_empty=False):
    """
    Asks the user for a path.
    check_exists: None (don't check), 'warn' (warn if not found), 'require' (error if not found)
    is_dir: If True, check if it's a directory (only if check_exists is active).
    allow_empty: If True, allows returning an empty string.
    """
    prompt_text = f"{prompt}"
    if default:
        prompt_text += f" [{default}]"
    prompt_text += ": "

    while True:
        try:
            user_input = input(prompt_text).strip()
            path = user_input if user_input else default

            if not path:
                if allow_empty:
                    return ""
                else:
                    print("Path cannot be empty.")
                    continue

            # Normalize path for consistency
            try:
                path = os.path.normpath(path)
            except ValueError:
                print(f"Invalid characters in path: {path}")
                continue # Ask again if path normalization fails

            if check_exists:
                exists = os.path.exists(path)
                is_correct_type = True
                if exists and is_dir:
                    is_correct_type = os.path.isdir(path)
                elif exists and not is_dir:
                     is_correct_type = os.path.isfile(path)

                if not exists:
                    if check_exists == 'require':
                        print(f"Error: Required path not found: {path}")
                        continue # Ask again
                    elif check_exists == 'warn':
                        print(f"Warning: Path not found: {path}")
                elif not is_correct_type:
                     type_str = "directory" if is_dir else "file"
                     if check_exists == 'require':
                          print(f"Error: Path exists but is not a {type_str}: {path}")
                          continue
                     elif check_exists == 'warn':
                         print(f"Warning: Path exists but is not a {type_str}: {path}")

            return path # Path is valid or warning was ignored
        except EOFError:
             print("\nInput aborted.")
             print("\nBye!")
             sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            print("\nBye!")
            sys.exit(1)


def ask_bool(prompt, default=True):
    """Asks a Yes/No question."""
    options = "[Y/n]" if default else "[y/N]"
    prompt_text = f"{prompt} {options}: "

    while True:
        try:
            user_input = input(prompt_text).strip().lower()
            if not user_input:
                return default
            if user_input in ['y', 'yes']:
                return True
            if user_input in ['n', 'no']:
                return False
            print("Please answer 'yes' or 'no' (or press Enter for default).")
        except EOFError:
             print("\nInput aborted.")
             print("\nBye!")
             sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            print("\nBye!")
            sys.exit(1)


def ask_choice(prompt, options, default=None):
    """Asks the user to choose from a list of options."""
    print(prompt)
    for i, option in enumerate(options):
        print(f"  {i+1}) {option}")

    default_index = -1
    if default in options:
        default_index = options.index(default)
        prompt_text = f"Enter choice number [{default_index + 1} - {default}]: "
    else:
        prompt_text = "Enter choice number: "

    while True:
        try:
            user_input = input(prompt_text).strip()
            if not user_input and default_index != -1:
                return options[default_index]
            if not user_input:
                 if default_index != -1: # Check if default exists even if user hit Enter without default shown
                     return options[default_index]
                 else:
                     print("Please make a selection.")
                     continue

            choice_index = int(user_input) - 1
            if 0 <= choice_index < len(options):
                return options[choice_index]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except EOFError:
             print("\nInput aborted.")
             print("\nBye!")
             sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            print("\nBye!")
            sys.exit(1)


def validate_product_version(prompt, app_version, default=None, allow_empty=False):
    """Verify the product version format."""
    """Product Version must be in the format X.X.X.X (four numbers separated by dots)"""
    prompt_text = f"{prompt}"
    if default is not None:
        prompt_text += f" [{default}]"
    prompt_text += ": "

    while True:
        try:
            user_input = input(prompt_text).strip()
            # Validate first, before checking other conditions
            if user_input and not re.match(r'^\d+\.\d+\.\d+\.\d+$', user_input):
                print("Error: Product Version must be in the format 'X.X.X.X' (four numbers separated by dots).")
                # Suggest a corrected version based on app_version if available
                if app_version and re.match(r'^\d+\.\d+\.\d+$', app_version):
                     suggested_version = f"{app_version}.0"
                     print(f"Suggestion based on App Version: {suggested_version}")
                     # Optionally, you could ask if they want to use the suggestion or re-enter
                continue # Ask again after showing the error

            # Now handle the input/default/empty logic
            if user_input: # If user typed something valid, return it
                return user_input
            elif default is not None: # If user pressed Enter AND there is a default, return default
                # Also validate the default if it's being used
                if not re.match(r'^\d+\.\d+\.\d+\.\d+$', default):
                     print(f"Warning: Default value '{default}' is not in the correct format 'X.X.X.X'.")
                     # Decide how to handle invalid default - here we ask again
                     print("Please enter a valid version.")
                     continue
                return default
            elif allow_empty: # If user pressed Enter, there is NO default, BUT empty is allowed
                return "" # Return the empty string
            else: # If user pressed Enter, there is NO default, and empty is NOT allowed
                print("Input cannot be empty.")
        except EOFError:
            print("\nInput aborted.")
            print("\nBye!")
            sys.exit(1)
        except KeyboardInterrupt:
             print("\nOperation cancelled by user.")
             print("\nBye!")
             sys.exit(1)
             

# --- NSIS Template ---
# Uses Python's f-string formatting. Variables like {app_name} are placeholders.
NSI_TEMPLATE = """
; NSIS script generated with NSIS Script Generator
; © {current_year} Thibault Savenkoff
; Generated on: {generation_date}

!include MUI2.nsh

; --- Application Info ---
Name "{app_name}"
OutFile "{output_installer_name}"
InstallDir "{install_dir_base}\\{install_dir_name}"
InstallDirRegKey {adminregistry} "{install_path_reg_key}" "Install_Dir"
BrandingText "{branding}"

; --- Version Information (for EXE properties) ---
VIProductVersion "{product_version}"
VIAddVersionKey "ProductName" "{app_name}"
VIAddVersionKey "CompanyName" "{publisher}"
VIAddVersionKey "LegalCopyright" "Copyright (c) {current_year} {publisher}"
VIAddVersionKey "FileDescription" "{app_name} Installer"
VIAddVersionKey "FileVersion" "{app_version}"
VIAddVersionKey "ProductVersion" "{product_version}"

; --- Interface Settings ---
{request_execution_level}
{set_compressor_command}

; --- Variables ---
Var StartMenuFolder

; --- MUI Settings ---
{mui_defines}

; --- Pages ---
{page_welcome}
{page_license}
{page_directory}
!insertmacro MUI_PAGE_INSTFILES
{page_finish}

; --- Uninstaller Pages ---
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; --- Language Settings ---
; NSIS will show a language selection dialog if multiple languages are loaded.
{language_macros}

; --- Functions ---
Function .onInit
  ; Set Start Menu Folder variable
  StrCpy $StartMenuFolder "{start_menu_folder}"
FunctionEnd

; --- Installation Section ---
Section "Install" SecInstall
  SetOutPath $INSTDIR
  SetOverwrite ifnewer

  ; --- Files ---
  ; NSIS uses backslashes in paths within the script
  File /r "{source_dir_nsis}\\*.*"

  ; --- Registry ---
  WriteRegStr {adminregistry} "{install_path_reg_key}" "Install_Dir" "$INSTDIR"
  WriteRegStr {adminregistry} "{uninstall_reg_key}" "DisplayName" "{app_name} (remove only)"
  WriteRegStr {adminregistry} "{uninstall_reg_key}" "UninstallString" '"$INSTDIR\\uninstall.exe"'
  WriteRegStr {adminregistry} "{uninstall_reg_key}" "QuietUninstallString" '"$INSTDIR\\uninstall.exe" /S'
  {uninstall_icon_reg}
  WriteRegStr {adminregistry} "{uninstall_reg_key}" "Publisher" "{publisher}"
  WriteRegStr {adminregistry} "{uninstall_reg_key}" "DisplayVersion" "{app_version}"
  WriteRegStr {adminregistry} "{uninstall_reg_key}" "URLInfoAbout" "{website}"
  WriteRegDWORD {adminregistry} "{uninstall_reg_key}" "NoModify" 1
  WriteRegDWORD {adminregistry} "{uninstall_reg_key}" "NoRepair" 1

  ; --- Uninstaller ---
  WriteUninstaller "$INSTDIR\\uninstall.exe"

  ; --- Shortcuts ---
{create_shortcuts_block}

SectionEnd

; --- Uninstallation Section ---
Section "Uninstall" SecUninstall
  ; --- Remove Shortcuts ---
{remove_shortcuts_block}

  ; --- Remove Files ---
  Delete "$INSTDIR\\uninstall.exe"
  RMDir /r "$INSTDIR"

  ; --- Remove Registry Keys ---
  DeleteRegKey {adminregistry} "{uninstall_reg_key}"
  DeleteRegKey {adminregistry} "{install_path_reg_key}"

SectionEnd
"""

def generate_nsis_script_from_config(config):
    """Generates the NSIS script content based on the config dictionary."""
    context = {}
    context['generation_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    context['current_year'] = datetime.datetime.now().year
    context.update(config) # Directly use the collected config

    # --- Generate Language Macros ---
    lang_macros_lines = []
    if 'selected_languages' in config and config['selected_languages']:
        print(f"Debug: Languages selected for NSIS: {config['selected_languages']}") # Debug print
        for lang in config['selected_languages']:
            # Ensure language name is treated as a literal string in NSIS
            lang_macros_lines.append(f'!insertmacro MUI_LANGUAGE "{lang}"')
    else:
        # Fallback if something went wrong, though the input loop should prevent this
        print("Warning: No languages selected, defaulting to English.")
        lang_macros_lines.append('!insertmacro MUI_LANGUAGE "English"')

    context['language_macros'] = "\n".join(lang_macros_lines)

    # --- Process specific fields ---
    context['install_dir_base'] = "$PROGRAMFILES64" if config.get('prefer_64bit', True) and config.get('request_admin', True) else "$PROGRAMFILES" if config.get('request_admin', False) else "$LOCALAPPDATA"
    context['request_execution_level'] = "RequestExecutionLevel admin" if config.get('request_admin', True) else "RequestExecutionLevel user"
    context['adminregistry'] = "HKLM" if config.get('request_admin', True) else "HKCU"

    # Compression
    comp = config.get('compression', 'lzma').lower()
    solid = config.get('solid_compression', True)
    context['set_compressor_command'] = f"SetCompressor {'/SOLID ' if solid else ''}{comp}"

    # MUI Defines
    mui_defines = ["!define MUI_ABORTWARNING"]
    if config.get('license_file') and os.path.exists(config['license_file']):
        if config['license_file'].lower().endswith(".rtf"):
            mui_defines.append(f'!define MUI_LICENSEPAGE_CHECKBOX') # Optional checkbox for RTF
    else:
        # Disable license page if file doesn't exist, even if user said yes during prompt
        config['show_license_page'] = False # Ensure consistency

    if config.get('installer_icon') and os.path.exists(config['installer_icon']):
        mui_defines.append(f'!define MUI_ICON "{config["installer_icon"]}"')
    if config.get('uninstaller_icon') and os.path.exists(config['uninstaller_icon']):
        mui_defines.append(f'!define MUI_UNICON "{config["uninstaller_icon"]}"')
    elif config.get('installer_icon') and os.path.exists(config['installer_icon']): # Fallback
        mui_defines.append(f'!define MUI_UNICON "{config["installer_icon"]}"')
    context['mui_defines'] = "\n".join(mui_defines)

    # UI Pages
    context['page_welcome'] = "!insertmacro MUI_PAGE_WELCOME" if config.get('show_welcome_page', True) else "; Welcome page disabled"
    context['page_finish'] = "!insertmacro MUI_PAGE_FINISH" if config.get('show_finish_page', True) else "; Finish page disabled"
    context['page_directory'] = "!insertmacro MUI_PAGE_DIRECTORY" if config.get('show_directory_page', True) else "; Directory page disabled"
    # Correctly handle license page visibility based on file existence and user choice
    context['page_license'] = f'!insertmacro MUI_PAGE_LICENSE "{config["license_file"]}"' if config.get('show_license_page', False) and config.get('license_file') else '; License page disabled or no file specified/found'

    # Start Menu Folder Logic (already determined during input)
    context['start_menu_folder'] = config['start_menu_folder']

    # Prepare path for NSIS File command (needs backslashes)
    context['source_dir_nsis'] = config['source_dir'].replace("/", "\\")

    # Shortcut Creation Code
    create_shortcut_lines = []
    remove_shortcut_lines = []
    if config.get('request_admin', True):
         create_shortcut_lines.append("  SetShellVarContext all ; Install for all users")
         remove_shortcut_lines.append("  SetShellVarContext all ; Remove for all users")

    main_exe_path = f"$INSTDIR\\{config.get('main_executable', 'MissingExecutable.exe')}"
    app_name = config.get('app_name', 'MyApp')
    sm_folder_var = "$StartMenuFolder" # Use the variable defined in .onInit

    if config.get('create_startmenu_shortcut', True):
        sm_link = f"$SMPROGRAMS\\{sm_folder_var}\\{app_name}.lnk"
        create_shortcut_lines.extend([
            f'  ; Create Start Menu Shortcuts',
            f'  CreateDirectory "$SMPROGRAMS\\{sm_folder_var}"',
            f'  CreateShortCut "{sm_link}" "{main_exe_path}" "" "{main_exe_path}" 0'
        ])
        remove_shortcut_lines.extend([
            f'  ; Remove Start Menu Shortcuts',
            f'  Delete "{sm_link}"',
            f'  RMDir "$SMPROGRAMS\\{sm_folder_var}" ; Only removes if empty',
        ])

    if config.get('create_desktop_shortcut', True):
        desktop_link = f"$DESKTOP\\{app_name}.lnk"
        create_shortcut_lines.append(f'  ; Create Desktop Shortcut')
        create_shortcut_lines.append(f'  CreateShortCut "{desktop_link}" "{main_exe_path}" "" "{main_exe_path}" 0')
        remove_shortcut_lines.append(f'  ; Remove Desktop Shortcut')
        remove_shortcut_lines.append(f'  Delete "{desktop_link}"')

    context['create_shortcuts_block'] = "\n".join(create_shortcut_lines) if create_shortcut_lines else "  ; No shortcuts configured"
    context['remove_shortcuts_block'] = "\n".join(remove_shortcut_lines) if remove_shortcut_lines else "  ; No shortcuts configured"


    # Uninstall Icon Registry Entry
    uninst_icon_path_reg = None
    # Prefer specified uninstaller icon if it exists
    if config.get('uninstaller_icon') and os.path.exists(config['uninstaller_icon']):
        uninst_icon_path_reg = config['uninstaller_icon']
    # Fallback to installer icon if it exists
    elif config.get('installer_icon') and os.path.exists(config['installer_icon']):
         uninst_icon_path_reg = config['installer_icon']

    if uninst_icon_path_reg:
         # Use absolute path for registry DisplayIcon if possible for robustness
         try:
             abs_icon_path = os.path.abspath(uninst_icon_path_reg).replace("\\", "\\\\") # Escape backslashes for registry string
             context['uninstall_icon_reg'] = f'WriteRegStr {context['adminregistry']} "{config["uninstall_reg_key"]}" "DisplayIcon" "{abs_icon_path}"'
         except Exception: # Handle potential issues with abspath
             main_exe = config.get("main_executable", "?.exe").replace("\\", "\\\\")
             context['uninstall_icon_reg'] = f'WriteRegStr {context['adminregistry']} "{config["uninstall_reg_key"]}" "DisplayIcon" "$INSTDIR\\\\{main_exe}" ; Default icon due to path issue'
    else: # Default to main executable within install dir
         main_exe = config.get("main_executable", "?.exe").replace("\\", "\\\\")
         context['uninstall_icon_reg'] = f'WriteRegStr {context['adminregistry']} "{config["uninstall_reg_key"]}" "DisplayIcon" "$INSTDIR\\\\{main_exe}"'


    # --- Format the template ---
    try:
        # Ensure all placeholders are handled
        final_script = NSI_TEMPLATE.format(**context)
        return final_script
    except KeyError as e:
        print(f"\nError: Missing configuration key needed for template: {e}", file=sys.stderr)
        print("Context keys available:", context.keys())
        return None
    except Exception as e:
         print(f"\nError generating NSIS script: {e}", file=sys.stderr)
         return None


# --- Main Execution ---
if __name__ == "__main__":
    # Initialize Tkinter but hide the root window
    root = tk.Tk()
    root.withdraw()

    print("--- NSIS Script Generator ---")
    print("Please answer the following questions to configure your installer.")
    print("Press Enter to accept the default value in brackets [].\n")

    config = {}

    # --- Application Info ---
    print("\n--- Basic Information ---")
    config['app_name'] = ask_string("Application Name", default="My Application")
    config['app_version'] = ask_string("Application Version (Only Numbers!)", default="1.0.0")
    config['product_version'] = validate_product_version(
        "Product Version (Four Numbers Required!)",
        app_version=config['app_version'],
        default=f"1.0.0.0"
    )
    config['publisher'] = ask_string("Publisher Name", default="My Company")
    config['website'] = ask_string("Application Website (optional, for Add/Remove Programs)", default="")

    # --- File Paths ---
    print("\n--- File Paths ---")

    # Use Tkinter for source directory - Directly open dialog
    print("Select the directory containing ALL files/folders to install...")
    source_dir_selected = filedialog.askdirectory(title="Select Source Directory")
    if not source_dir_selected:
        print("Source directory selection cancelled. Exiting.")
        sys.exit(1)
    config['source_dir'] = os.path.normpath(source_dir_selected)
    print(f"    Source Directory: {config['source_dir']}")

    # Directly open file dialog for main executable
    print("Select the main executable file (must be inside the source directory)...")
    main_exe_full_path = None
    exe_selected = filedialog.askopenfilename(
        title="Select Main Executable",
        initialdir=config['source_dir'], # Start in the source directory
        filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
    )
    if exe_selected:
        # Validate that the selected file is within the source directory
        if os.path.dirname(os.path.normpath(exe_selected)) == config['source_dir']:
            config['main_executable'] = os.path.basename(exe_selected)
            main_exe_full_path = exe_selected # Store full path for potential later use
            print(f"    Selected Main Executable: {config['main_executable']}")
        else:
            messagebox.showerror("Error", "The selected executable must be inside the source directory.")
            print("Invalid executable selection (not in source directory). Proceeding without a main executable.")
            config['main_executable'] = None
    else:
        print("Main executable selection cancelled. Proceeding without a main executable.")
        config['main_executable'] = None


    # Directly open file dialog for license file
    print("Select the license file ('.txt' or '.rtf', optional)...")
    license_selected = filedialog.askopenfilename(
        title="Select License File (Optional)",
        filetypes=[("Text files", "*.txt"), ("Rich Text Format", "*.rtf"), ("All files", "*.*")]
    )
    if license_selected:
        config['license_file'] = os.path.normpath(license_selected)
        print(f"Selected License File: {config['license_file']}")
    else:
        print("License file selection cancelled or skipped.")
        config['license_file'] = "" # Set to empty string if cancelled


    # Directly open file dialog for installer icon
    print("Select the installer icon file ('.ico', optional)...")
    icon_selected = filedialog.askopenfilename(
        title="Select Installer Icon (Optional)",
        filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
    )
    if icon_selected:
        config['installer_icon'] = os.path.normpath(icon_selected)
        print(f"Selected Installer Icon: {config['installer_icon']}")
    else:
        print("Installer icon selection cancelled or skipped.")
        config['installer_icon'] = "" # Set to empty string if cancelled


    # Directly open file dialog for uninstaller icon
    print("Select the uninstaller icon file ('.ico', optional, defaults to installer icon or none)...")
    unicon_selected = filedialog.askopenfilename(
        title="Select Uninstaller Icon (Optional)",
        filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
    )
    if unicon_selected:
        config['uninstaller_icon'] = os.path.normpath(unicon_selected)
        print(f"Selected Uninstaller Icon: {config['uninstaller_icon']}")
    else:
        print("Uninstaller icon selection cancelled or skipped.")
        config['uninstaller_icon'] = "" # Set to empty string if cancelled


    default_output_name = f"{config['app_name'].replace(' ', '_')}_v{config['app_version']}_Setup.exe"
    config['output_installer_name'] = ask_string("Filename for the final installer executable", default=default_output_name)
    if not config['output_installer_name'].lower().endswith(".exe"):
         config['output_installer_name'] += ".exe"


    # --- Installation Options ---
    print("\n--- Installation Options ---")

    config['install_dir_name'] = ask_string(
        "Installation folder name (e.g., 'My App' under Program Files/Local App Data)",
        default=config['app_name']
    )
    config['request_admin'] = ask_bool("Require Administrator privileges (needed for Program Files)?", default=True)
    if config['request_admin'] == True:
        config['prefer_64bit'] = ask_bool("Prefer 64-bit Program Files (if available)?", default=True)
    else:
        config['prefer_64bit'] = False
    config['compression'] = ask_choice(
        "Compression method",
        options=['lzma', 'zlib', 'bzip2'],
        default='lzma'
    )
    config['solid_compression'] = ask_bool("Use solid compression (better ratio, slower build/install)?", default=True)

    # --- Shortcuts ---
    print("\n--- Shortcuts ---")
    config['create_startmenu_shortcut'] = ask_bool("Create Start Menu shortcut?", default=True)
    if config['create_startmenu_shortcut']:
        sm_choice = ask_choice(
            "Start Menu Folder Name:",
            options=["Use Publisher Name", "Use Application Name", "Custom"],
            default="Use Publisher Name"
        )
        if sm_choice == "Use Publisher Name":
            config['start_menu_folder'] = config['publisher']
        elif sm_choice == "Use Application Name":
            config['start_menu_folder'] = config['app_name']
        else:
            config['start_menu_folder'] = ask_string("Enter Custom Start Menu Folder Name", default=config['publisher'])
    else:
         config['start_menu_folder'] = "" # Set empty if no shortcut

    config['create_desktop_shortcut'] = ask_bool("Create Desktop shortcut?", default=True)

    # --- Registry ---
    print("\n--- Registry ---")

    app_name_safe = ''.join(filter(str.isalnum, config['app_name']))
    publisher_safe = ''.join(filter(str.isalnum, config['publisher']))
    default_uninstall_key = f"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name_safe}"
    config['uninstall_reg_key'] = ask_string("Registry key for Uninstall Information (must be unique!)", default=default_uninstall_key)

    default_install_path_key = f"Software\\{publisher_safe}\\{app_name_safe}"
    config['install_path_reg_key'] = ask_string("Registry key to store Installation Path (optional but recommended)", default=default_install_path_key)

    # --- Language ---
    print("\n--- Language ---")

    selected_languages = []
    print("Enter the installer languages one by one.")
    print("These MUST match NSIS language file names (e.g., English, German, French).")
    print("See NSIS\\Contrib\\Language files directory for available names.")
    # Get the primary/default language first
    while True:
        primary_lang = ask_string("Enter the primary/default language", default="English").capitalize()
        if primary_lang:
            selected_languages.append(primary_lang)
            break
        else:
            print("You must specify at least one language.")

    # Ask for additional languages
    while True:
        current_langs_str = ', '.join(selected_languages)
        next_lang = ask_string(
            f"Add another language? Current: {current_langs_str} (Leave blank to finish)",
            allow_empty=True
        ).capitalize()
        if not next_lang:
            break # User finished adding languages
        if next_lang not in selected_languages:
            # Basic check - NSIS names usually don't have spaces or numbers
            if ' ' in next_lang or any(char.isdigit() for char in next_lang):
                 print(f"Warning: '{next_lang}' seems like an unusual NSIS language name. Ensure it matches a .nlf file.")
            selected_languages.append(next_lang)
            print(f"Added '{next_lang}'. Current: {', '.join(selected_languages)}")
        else:
            print(f"'{next_lang}' is already in the list.")

    config['selected_languages'] = selected_languages # Store the list

    # --- UI ---
    print("\n--- UI ---")

    config['branding'] = ask_string("Branding Text", default=f"{config['publisher']} - {config['app_name']} v{config['app_version']}")
    config['show_welcome_page'] = ask_bool("Show Welcome page?", default=True)
    # Check license file existence *after* potential dialog selection
    license_exists = config.get('license_file') and os.path.exists(config['license_file'])
    if license_exists:
        config['show_license_page'] = ask_bool("Show License page?", default=True)
    else:
        # No need to warn here as the user explicitly cancelled or didn't select
        config['show_license_page'] = False # Force false if no valid file selected
    config['show_directory_page'] = ask_bool("Show Directory selection page?", default=True)
    config['show_finish_page'] = ask_bool("Show Finish page?", default=True)


    # --- Generate Script ---
    print("\n--- Generating Script ---")

    nsis_script_content = generate_nsis_script_from_config(config)

    if nsis_script_content:
        default_nsi_filename = f"{config['app_name'].lower().replace(' ', '_').replace('.', '')}.nsi"

        # Use Tkinter Save As dialog
        print("Select where to save the generated NSIS script...")
        nsi_output_file = filedialog.asksaveasfilename(
            title="Save NSIS Script As",
            initialfile=default_nsi_filename,
            defaultextension=".nsi",
            filetypes=[("NSIS Script", "*.nsi"), ("All Files", "*.*")]
        )

        if not nsi_output_file:
            print("Save operation cancelled. Exiting.")
            print("\nBye!")
            sys.exit(1)

        try:
            with open(nsi_output_file, "w", encoding="utf-8", newline='\r\n') as f: # Use Windows line endings for NSIS
                f.write(nsis_script_content)
            print(f"\nSuccessfully generated '{nsi_output_file}'")

            # --- Optional: Offer to compile ---
            if ask_bool("\nAttempt to compile the script now using 'makensis'?", default=True):
                try:
                    print(f"Running: makensis \"{os.path.abspath(nsi_output_file)}\"")
                    # Use shell=True cautiously, might be needed for finding makensis in PATH on Windows easily
                    process = subprocess.run(['makensis', os.path.abspath(nsi_output_file)],
                                             capture_output=True, text=True, check=False,
                                             shell=(sys.platform == "win32"), encoding='utf-8', errors='replace')
                    print("\n--- Compilation Output ---")
                    print(process.stdout if process.stdout else "(No standard output)")
                    if process.stderr:
                         print("--- Compilation Errors/Warnings ---")
                         print(process.stderr)

                    if process.returncode == 0:
                         print("--- Compilation Successful ---")
                         # Construct expected output path relative to the NSI file location
                         output_installer_path = os.path.join(os.path.dirname(os.path.abspath(nsi_output_file)), config['output_installer_name'])
                         if os.path.exists(output_installer_path):
                              print(f"Installer created: {output_installer_path}")
                         else:
                              # NSIS might put output elsewhere depending on script logic/cwd, or OutFile path
                              print(f"Installer '{config['output_installer_name']}' may have been created.")
                              print("Check the compilation output above or the directory containing the NSI script.")
                    else:
                         print(f"--- Compilation Failed (exit code {process.returncode}) ---")

                except FileNotFoundError:
                    print("\nError: 'makensis.exe' command not found.")
                    print("Ensure NSIS is installed and 'makensis.exe' is in your system's PATH environment variable.")
                    messagebox.showerror("Compilation Error", "'makensis.exe' command not found.\nEnsure NSIS is installed and in your system's PATH.")
                except Exception as e:
                    print(f"\nAn error occurred during compilation: {e}")
                    messagebox.showerror("Compilation Error", f"An error occurred during compilation:\n{e}")
            else:
                 print("\nTo compile the script manually, open a terminal/command prompt,")
                 print("navigate to this directory, and run:")
                 print(f"  makensis \"{nsi_output_file}\"")
                 print("\nBye!")

        except IOError as e:
            print(f"\nError writing file '{nsi_output_file}': {e}", file=sys.stderr)
            messagebox.showerror("File Error", f"Error writing file '{nsi_output_file}':\n{e}")
            sys.exit(1)
    else:
        print("\nNSIS script generation failed due to errors.", file=sys.stderr)
        messagebox.showerror("Generation Error", "NSIS script generation failed. Check console output for details.")
        sys.exit(1)
