# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os, sys, django



sys.path.insert(0, os.path.abspath('../..'))


project = 'Hard Second Project'
copyright = '2026, MSHP Team'
author = 'MSHP Team'
release = '0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath('../..'))

# 2. Указываем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') # Убедитесь, что 'config.settings' — верный путь
django.setup()

# --- General configuration ---

extensions = [
    'sphinx.ext.autodoc',      # Включает автоматическое сканирование docstrings
    'sphinx.ext.viewcode',     # Добавляет ссылки на исходный код
    'sphinx.ext.napoleon',     # (Опционально) Поддержка docstrings в стиле Google/NumPy
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


def skip_django_members(app, what, name, obj, skip, options):
    # 1. Скрываем всё, что начинается с подчеркивания (внутренние методы)
    if name.startswith('_'):
        return True

    # 2. Список "черного списка" для технических имен Django
    exclusions = {
        'DoesNotExist', 'MultipleObjectsReturned', 'objects',
        'id', 'pk', 'base_objects', 'NotUpdated', 'clean', 'save'
    }
    if name in exclusions:
        return True

    # 3. Скрываем все внешние ключи с окончанием _id
    if name.endswith('_id'):
        return True

    # 4. Скрываем системные методы навигации Django по датам
    if name.startswith('get_next_by') or name.startswith('get_previous_by'):
        return True

    # 5. ГЛАВНОЕ: Скрываем атрибут, если у него нет вашего комментария (docstring)
    # или если этот комментарий — стандартная заглушка Django.
    doc = getattr(obj, '__doc__', '') or ''

    # Список стандартных фраз Django, которые мы не хотим видеть
    django_garbage = [
        "A wrapper for a deferred-loading field",
        "Accessor to the related object",
        "The descriptor for the file attribute",
        "Hook for doing any extra model-wide validation",
        "Most of the implementation is delegated to a dynamically defined manager"
    ]

    if any(garbage in doc for garbage in django_garbage):
        return True

    # Если docstring пустой и это не класс/функция — скорее всего, это системное поле
    if not doc and what == "attribute":
        return True

    return skip


def setup(app):
    app.add_css_file('custom.css')
    app.connect('autodoc-skip-member', skip_django_members)