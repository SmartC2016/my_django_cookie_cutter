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
                    closing_bracket_index - 1, f'    # local apps\n    "{new_app}",\n'
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


def create_folder(folder_name):
    """creates a folder"""
    os.makedirs(folder_name, exist_ok=True)


def create_readme(folder_name):
    """creates the README.md file"""
    with open(
        os.path.join(folder_name, "README.md"), "w", encoding="utf-8"
    ) as readme_file:
        current_date = datetime.now().strftime("%Y-%m-%d")
        readme_file.write(
            f"{folder_name} - {current_date} - copyright by Christian Hetmann\n"
        )


def create_virtualenv_and_django_project(
    folder_name, django_project_name, django_app_name
):
    os.chdir(folder_name)
    try:
        subprocess.run(["pipenv", "install", "django"], check=True)
        print()
        subprocess.run(["pipenv", "install", "pytest"], check=True)
        print()
        subprocess.run(
            ["pipenv", "run", "django-admin", "startproject", django_project_name, "."],
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


def create_tailwind_config(folder_name):
    tailwind_config_path = os.path.join(folder_name, "tailwind.config.js")
    if os.path.exists(tailwind_config_path):
        return  # If the file already exists, don't overwrite it

    with open(tailwind_config_path, "w", encoding="utf-8") as tailwind_config:
        tailwind_config.write(
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
        )


if __name__ == "__main__":
    folder_name = input("Enter folder name: ")
    django_project_name = input("Enter Django project name: ")
    django_app_name = input("Enter Django app name: ")

    # Construct absolute paths
    absolute_folder_path = os.path.abspath(folder_name)

    create_folder(absolute_folder_path)
    create_readme(absolute_folder_path)
    create_tailwind_config(absolute_folder_path)
    create_virtualenv_and_django_project(
        absolute_folder_path, django_project_name, django_app_name
    )

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
    settings_modifier.write_settings()
