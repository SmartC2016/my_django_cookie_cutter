#!/usr/bin/env python3

""" This script does the following:
* create a folder with a given name
* in that folder create a virtual environment using pipenv
* in that virtual environment create a django project with a given name and a django app
* create a README.md with the first line
"""

# pylint: disable=C0103
# pylint: disable=C0115
# pylint: disable=C0116
# pylint: disable=W0621

import os
import subprocess
import json
from datetime import datetime


class DjangoSettingsModifier:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.lines = []

    def read_settings(self):
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Settings file '{self.settings_file}' not found.")
            exit()

    def write_settings(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            f.write("".join(self.lines))

    def add_to_installed_apps(self, new_app):
        installed_apps_index = None
        for i, line in enumerate(self.lines):
            if line.startswith("INSTALLED_APPS"):
                installed_apps_index = i
                break

        if installed_apps_index is not None:
            # Find the closing bracket of INSTALLED_APPS list
            closing_bracket_index = None
            for j in range(installed_apps_index, len(self.lines)):
                if "]" in self.lines[j]:
                    closing_bracket_index = j
                    break

            if closing_bracket_index is not None:
                # Insert the new app before the closing bracket
                self.lines.insert(
                    closing_bracket_index,
                    "    # local apps\n"  # Comment line
                    f'    "{new_app}",\n',  # New app line
                )
                print("App added successfully to INSTALLED_APPS!")
            else:
                print("Error: Closing bracket of INSTALLED_APPS not found.")
        else:
            print("INSTALLED_APPS not found in settings.py")
        print()

    def update_time_zone(self, new_time_zone):
        time_zone_index = None
        for i, line in enumerate(self.lines):
            if line.startswith("TIME_ZONE"):
                time_zone_index = i
                break

        if time_zone_index is not None:
            self.lines[time_zone_index] = f'TIME_ZONE = "{new_time_zone}"\n'
            print("Time zone updated successfully!")
        else:
            print("TIME_ZONE not found in settings.py")

    def update_language_code(self, new_language_code):
        language_code_index = None
        for i, line in enumerate(self.lines):
            if line.startswith("LANGUAGE_CODE"):
                language_code_index = i
                break

        if language_code_index is not None:
            self.lines[language_code_index] = f'LANGUAGE_CODE = "{new_language_code}"\n'
            print("Language code updated successfully!")
        else:
            print("LANGUAGE_CODE not found in settings.py")

    def update_static_file_dir(self):
        """Add 'STATICFILES_DIRS = [BASEDIR / "static"]' to settings.py"""
        static_index = None
        for i, line in enumerate(self.lines):
            if line.startswith("STATIC_URL"):
                static_index = i
                break
        if static_index is not None:
            self.lines.insert(
                static_index + 1,
                'STATICFILES_DIRS = [BASE_DIR / "static"]\n',
            )
            print("Staticfiles inserted successfully")
        else:
            print("Staticfiles inserted NOT successfully")
            exit(1)


class FolderCreator:
    def __init__(self, folder_name):
        self.folder_name = folder_name

    def create_folder(self):
        """Create the Django Project Folder"""
        if os.path.exists(self.folder_name):
            print(f"Error: Folder '{self.folder_name}' already exists.")
            exit(1)
        else:
            os.makedirs(self.folder_name)

    def create_static_folders(self):
        """Creates static folders inside the main folder"""
        static_folder = os.path.join(self.folder_name, "static")
        os.makedirs(static_folder, exist_ok=True)

        static_subfolders = ["css", "js", "fonts"]
        for subfolder in static_subfolders:
            subfolder_path = os.path.join(static_folder, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)

        self.create_main_css()

    def create_main_css(self):
        """Creates main.css file with content"""
        main_css_path = os.path.join(self.folder_name, "static", "css", "main.css")
        if not os.path.exists(main_css_path):
            with open(main_css_path, "w", encoding="utf-8") as main_css_file:
                main_css_file.write(
                    "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n"
                )
            print("main.css created successfully")
        else:
            print("Error creating static/css/main.css")
            print("File already exists!")

    def create_readme(self):
        """creates the README.md file"""
        with open(
            os.path.join(self.folder_name, "README.md"), "w", encoding="utf-8"
        ) as readme_file:
            current_date = datetime.now().strftime("%Y-%m-%d")
            readme_file.write(
                f"{self.folder_name} - {current_date} - copyright by Christian Hetmann\n\n"
            )
            readme_file.write(
                """ 
Oben im base.html muss {% load static %} angegeben werden.

Je nachdem ob Alpine oder HTMX installiert wurde, muss es dann entsprechend in dem base.html hinzugefügt werden.

Für Alpine.js: oben im <head> ... <script defer src="{% static 'js/alpine/cdn.min.js' %}"></script> ... <head>

Für Tailwind CSS: <head> ... <link rel="stylesheet" href="{% static 'css/main.min.css' %}">

Bei HTMX: Innerhalb des body tags, ganz unten: <script src="{% static 'js/htmx/htmx.min.js' %}"></script>

NPM-WATCH ist ja installiert. Daher in einem seperatem Terminal Fenster nun: "npm run watch" eingeben.

GGf. muss im Dokument noch Prettier als DEFAULT Formatter ausgewählt werden, damit das prettier-plugin-tailwindcss zu sortieren der Css classes funktioniert.

                """
            )

    def create_pylint_config(self):
        "Creates the .pylintrc and sets the max line length"
        pylintrc_file = os.path.join(self.folder_name, ".pylintrc")
        if not os.path.exists(pylintrc_file):
            with open(pylintrc_file, "w", encoding="utf-8") as p_file:
                p_file.write("[FORMAT]\nmax-line-length=140\n")
                print(".pylintrc with max-line-length=140 created created")
        else:
            print("Error creating '.pylintrc' file")

    def create_virtualenv_and_django_project(
        self, django_project_name, django_app_name
    ):
        """creates a virtual environment and Django project with the given names"""
        os.chdir(self.folder_name)
        try:
            subprocess.run(["pipenv", "install", "django"], check=True)
            print()
            subprocess.run(["pipenv", "install", "pytest"], check=True)
            print()
            subprocess.run(
                [
                    "pipenv",
                    "run",
                    "django-admin",
                    "startproject",
                    django_project_name,
                    ".",
                ],
                check=True,
            )
            print()
            subprocess.run(
                ["pipenv", "run", "python", "manage.py", "startapp", django_app_name],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            exit(1)

    def create_django_app_template_folders(self, django_app_name):
        """Creates template folders inside the django_app folder"""
        templates_folder = os.path.join(
            self.folder_name, django_app_name, "templates", django_app_name
        )
        os.makedirs(templates_folder, exist_ok=True)
        print(f"Templates folder in '{django_app_name}' created.")

    def create_postcss_config(self):
        """Creates postcss.config.js file"""
        postcss_config_path = os.path.join(self.folder_name, "postcss.config.js")
        if not os.path.exists(postcss_config_path):
            with open(
                postcss_config_path, "w", encoding="utf-8"
            ) as postcss_config_file:
                postcss_config_file.write(
                    """module.exports = {
    plugins: {
        tailwindcss: {},
        autoprefixer: {},
    }
}"""
                )
            print("postcss.config.js created successfully!")
        else:
            print("postcss.config.js already exists.")


class DjangoBrowserReloadInstaller:
    def __init__(self, folder_path, settings_file, django_project_name) -> None:
        self.settings_file = settings_file
        self.django_project_url_file = os.path.join(
            folder_path, django_project_name, "urls.py"
        )
        self.lines = []
        self.folder_path = folder_path
        self.install_django_browser_reload()
        self.read_settings()
        self.add_to_installed_apps()
        self.add_to_middleware()
        self.write_settings()
        self.update_urls_py()

    def read_settings(self):
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Settings file '{self.settings_file}' not found.")
            exit(1)

    def write_settings(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            f.write("".join(self.lines))

    def install_django_browser_reload(self):
        """Install django-browser-reload -> https://pypi.org/project/django-browser-reload/"""
        os.chdir(self.folder_path)
        try:
            subprocess.run(["pipenv", "install", "django-browser-reload"], check=True)
            print()
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            exit(1)

    def add_to_installed_apps(self):
        installed_apps_index = None
        for i, line in enumerate(self.lines):
            if line.startswith("INSTALLED_APPS"):
                installed_apps_index = i
                break

        if installed_apps_index is not None:
            # Find the closing bracket of INSTALLED_APPS list
            closing_bracket_index = None
            for j in range(installed_apps_index, len(self.lines)):
                if "]" in self.lines[j]:
                    closing_bracket_index = j
                    break

            if closing_bracket_index is not None:
                # Insert django-browser-reload app before the closing bracket
                self.lines.insert(
                    closing_bracket_index,
                    "    # 3rd party apps\n"  # Comment line
                    '    "django_browser_reload",\n',  # django-browser-reload
                )
                print("django-browser-reload added successfully to INSTALLED_APPS!")
            else:
                print("Error: Closing bracket of INSTALLED_APPS not found.")
        else:
            print("INSTALLED_APPS not found in settings.py")
        print()

    def add_to_middleware(self):
        middleware_index = None
        for i, line in enumerate(self.lines):
            if line.startswith("MIDDLEWARE"):
                middleware_index = i
                break

        if middleware_index is not None:
            # Find the closing bracket of MIDDLEWARE list
            closing_bracket_index = None
            for j in range(middleware_index, len(self.lines)):
                if "]" in self.lines[j]:
                    closing_bracket_index = j
                    break

            if closing_bracket_index is not None:
                # Insert django-browser-reload app before the closing bracket
                self.lines.insert(
                    closing_bracket_index,
                    "    # needed for django-browser-reload\n"  # Comment line
                    '    "django_browser_reload.middleware.BrowserReloadMiddleware",\n',  # django-browser-reload
                )
                print("django-browser-reload added successfully to MIDDLEWARE!")
            else:
                print("Error: Closing bracket of MIDDLEWARE not found.")
        else:
            print("MIDDLEWARE not found in settings.py")
        print()

    def update_urls_py(self):
        """changes the django project url file and adds django-browser-reload and also add include to the import statement"""
        if os.path.exists(self.django_project_url_file):
            with open(self.django_project_url_file, "r", encoding="utf-8") as url_file:
                content = url_file.readlines()

            django_urls_index = None
            for i, line in enumerate(content):
                if line.startswith("from django.urls"):
                    django_urls_index = i
                    break

            if django_urls_index is not None:
                content[django_urls_index] = "from django.urls import path, include\n"
                print("'include' successfully added to import statement!")
            else:
                print("'include' could not be imported!")
                exit(1)

            new_lines = "\n# added for django-browser-reload\n"
            new_lines += """urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))\n"""

            content += new_lines

            with open(self.django_project_url_file, "w", encoding="utf-8") as f:
                f.write("".join(content))
            print("django project urls.py UPDATED for django-browser-reload")
        else:
            print("Error adding django-browser-reload to urls.py")


class AlpineJSInstaller:
    def __init__(self, folder_path) -> None:
        self.folder_path = folder_path
        self.install_alpine()

    def install_alpine(self):
        """Install Alpine JS"""
        os.chdir(self.folder_path)
        print()
        print("Installing AlpineJS")
        try:
            subprocess.run(
                [
                    "npm",
                    "install",
                    "alpinejs",
                ],
                check=True,
            )
            print("AlpineJS installed successfully!")

            alpine_folder = os.path.join(self.folder_path, "static", "js", "alpine")
            os.makedirs(alpine_folder, exist_ok=True)

            package_json_path = os.path.join(self.folder_path, "package.json")
            if os.path.exists(package_json_path):
                with open(package_json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

            # Add the "scripts" key
            data["scripts"]["build"] = (
                data["scripts"]["build"]
                + "; cp node_modules/alpinejs/dist/cdn.min.js static/js/alpine/cdn.min.js"
            )
            with open(package_json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            print("package.json updated accordingly!")

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            exit(1)


class HTMXInstaller:
    def __init__(self, folder_path) -> None:
        self.folder_path = folder_path
        self.install_htmx()

    def install_htmx(self):
        """Install HTMX"""
        os.chdir(self.folder_path)
        print()
        print("Installing HTMX")
        try:
            subprocess.run(
                [
                    "npm",
                    "install",
                    "htmx.org",
                ],
                check=True,
            )
            print("HTMX installed successfully!")

            htmx_folder = os.path.join(self.folder_path, "static", "js", "htmx")
            os.makedirs(htmx_folder, exist_ok=True)

            package_json_path = os.path.join(self.folder_path, "package.json")
            if os.path.exists(package_json_path):
                with open(package_json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

            # Add the "scripts" key
            data["scripts"]["build"] = (
                data["scripts"]["build"]
                + "; cp node_modules/htmx.org/dist/htmx.min.js static/js/htmx/htmx.min.js"
            )
            with open(package_json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            print("package.json updated accordingly!")

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            exit(1)


class NPMRunBuild:
    def __init__(self, folder_path) -> None:
        print("Running 'npm run build' - Should not throw any errors!")
        os.chdir(folder_path)

        try:
            subprocess.run(
                [
                    "npm",
                    "run",
                    "build",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            exit(1)


class TailwindInstaller:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def install_tailwind(self):
        """Installs Tailwind CSS and tools locally"""
        print()
        print("Install Tailwind CSS and tools locally")
        os.chdir(self.folder_path)
        try:
            subprocess.run(
                [
                    "npm",
                    "install",
                    "-D",
                    "tailwindcss",
                    "postcss",
                    "postcss-cli",
                    "autoprefixer",
                    "npm-watch",
                    "prettier",  # new
                    "prettier-plugin-tailwindcss",  # new
                ],
                check=True,
            )
            print("Tailwind CSS installed successfully!")
            subprocess.run(
                [
                    "npx",
                    "tailwindcss",
                    "init",
                ],
                check=True,
            )
            print("Tailwind CSS NPX init successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            exit(1)

    def update_tailwind_config(self, django_app_name):
        """Updates tailwind.config.js file"""
        tailwind_config_path = os.path.join(self.folder_path, "tailwind.config.js")
        if os.path.exists(tailwind_config_path):
            with open(tailwind_config_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if "content:" in line:
                    # Find the line with 'content' and append the content string
                    lines[i] = (
                        f"  content: ['./{django_app_name}/templates/{django_app_name}/*.html'],\n"
                    )
                    break

            with open(tailwind_config_path, "w", encoding="utf-8") as file:
                file.write("".join(lines))
            print("Tailwind config updated successfully!")
        else:
            print("tailwind.config.js file not found.")

    def update_package_json(self, django_app_name):
        """Updates package.json file"""
        package_json_path = os.path.join(self.folder_path, "package.json")
        if os.path.exists(package_json_path):
            with open(package_json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Add the "scripts" key
            data["scripts"] = {
                "build": "postcss static/css/main.css -o static/css/main.min.css",
                "watch": "npm-watch",
            }

            # Add the "watch" key and sub-keys
            data["watch"] = {
                "build": {
                    "patterns": [f"{django_app_name}"],
                    "extensions": "html",
                    "quiet": "false",
                }
            }

            with open(package_json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            print("package.json updated successfully!")
        else:
            print("package.json file not found.")

    def create_and_setup_prettier_config(self):
        """Creates the .prettierrc file and sets needed configuration"""
        prettierrc_path = os.path.join(self.folder_path, ".prettierrc")

        data = {}
        data["tabWidth"] = 4
        data["useTabs"] = False
        data["plugins"] = ["prettier-plugin-tailwindcss"]
        data["trailingComma"] = "es5"
        data["semi"] = False
        with open(prettierrc_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        print(".prettierrc created and updated accordingly!")


if __name__ == "__main__":
    folder_name = input("Enter folder name for the Django app: ")
    django_project_name = input("Enter Django project name (e.g. core): ")
    django_app_name = input("Enter Django app name (e.g. pages): ")
    install_django_browser_reload = input(
        "Should Django-Browser-Reload be installed? [y/N] "
    )
    install_alpine = input("Should AlpineJS be installed? [y/N] ")
    install_htmx = input("Should HTMX be installed? [y/N] ")
    print()

    # Construct absolute paths
    absolute_folder_path = os.path.abspath(folder_name)

    folder_creator = FolderCreator(absolute_folder_path)
    folder_creator.create_folder()
    folder_creator.create_readme()
    folder_creator.create_virtualenv_and_django_project(
        django_project_name, django_app_name
    )
    folder_creator.create_django_app_template_folders(django_app_name)
    folder_creator.create_static_folders()
    folder_creator.create_pylint_config()
    folder_creator.create_postcss_config()

    print("Folder created with README.md and Django project setup completed.")

    # Construct absolute path to settings.py
    settings_file_path = os.path.join(
        absolute_folder_path, django_project_name, "settings.py"
    )
    new_app = f"{django_app_name}.apps.{django_app_name.capitalize()}Config"
    new_time_zone = "Europe/Berlin"
    new_language_code = "de"

    settings_modifier = DjangoSettingsModifier(settings_file_path)
    settings_modifier.read_settings()
    settings_modifier.add_to_installed_apps(new_app)
    settings_modifier.update_time_zone(new_time_zone)
    settings_modifier.update_language_code(new_language_code)
    settings_modifier.update_static_file_dir()
    settings_modifier.write_settings()

    # Install django-browser-reload
    if install_django_browser_reload.capitalize() == "Y":
        DjangoBrowserReloadInstaller(
            absolute_folder_path, settings_file_path, django_project_name
        )
    else:
        print("django-browser-reload will NOT be installed!")

    # Install Tailwind CSS
    tailwind_installer = TailwindInstaller(absolute_folder_path)
    tailwind_installer.install_tailwind()
    # Update tailwind.config.js
    tailwind_installer.update_tailwind_config(django_app_name)
    # Update package.json
    tailwind_installer.update_package_json(django_app_name)
    tailwind_installer.create_and_setup_prettier_config()

    if install_alpine.capitalize() == "Y":
        AlpineJSInstaller(absolute_folder_path)
    else:
        print("AlpineJS will NOT be installed!")
    if install_htmx.capitalize() == "Y":
        HTMXInstaller(absolute_folder_path)
    else:
        print("HTMX will NOT be installed!")
    NPMRunBuild(absolute_folder_path)


"""\
module.exports = {
  theme: {
    extend: {
      colors: {
        clifford: "#da373d",
      },
    },
  },
};"""
