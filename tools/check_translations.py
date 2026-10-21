#!/usr/bin/env python3
"""Check community translation files for Dreamforge RPG.

A translation file is translations/<code>.json:

    {
      "language": "fr",
      "name": "Français",
      "authors": ["github-user"],
      "strings": { "Forge": "Forge", "Salvage all": "Tout recycler" }
    }

Rules (a violation is an error unless noted):
  * the file is valid UTF-8 JSON and at most 2 MB
  * "language" matches ^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$ and equals the
    file name stem; ja, en and zh are built in and template.json is the
    template, so none of them may be used as a language code
  * "name" is a string of 1 to 40 characters
  * "authors", when present, is an array of strings
  * "strings" maps English source sentences to translations; an empty
    value counts as untranslated and is allowed
  * every non-empty value has the same {0} {1} ... placeholders as its
    key, the same rich text tags (<b> <i> <color=...> <size=...> and
    their closing tags) in kind and count, no http / www. / :// unless
    the key contains the same marker, no control characters other than
    newline and tab, and at most 4 * len(key) + 40 characters
  * with --template, keys missing from the template only produce a
    warning ("old key"), never a failure

Usage:
  python3 tools/check_translations.py [--template PATH] [--json] FILE...
  python3 tools/check_translations.py --coverage OUT.md [--template PATH] FILE...

A file named template.json in the FILE arguments is skipped, so the
glob translations/*.json can be passed as is.

Exit codes: 0 = all files passed, 1 = at least one file failed,
2 = usage error.
"""

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

LANGUAGE_RE = re.compile(r'^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$')
RESERVED_LANGUAGES = ('ja', 'en', 'zh', 'template')
PLACEHOLDER_RE = re.compile(r'\{(\d+)\}')
TAG_RE = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9]*)(=[^>]*)?>')
URL_MARKERS = ('http', 'www.', '://')
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_NAME_LENGTH = 40
VALUE_LENGTH_SLACK = 40
KEY_PREVIEW_LENGTH = 40


def preview(key):
    """First KEY_PREVIEW_LENGTH characters of a source string."""
    text = key[:KEY_PREVIEW_LENGTH]
    if len(key) > KEY_PREVIEW_LENGTH:
        text += '...'
    return text


def placeholder_text(numbers):
    if not numbers:
        return '(none)'
    return ', '.join('{%s}' % n for n in sorted(numbers, key=int))


def tag_counts(text):
    counts = Counter()
    for closing, name, _attribute in TAG_RE.findall(text):
        name = name.lower()
        counts[('/' + name) if closing else name] += 1
    return counts


def tag_text(counts):
    if not counts:
        return '(none)'
    return ', '.join('<%s> x%d' % (name, count) for name, count in sorted(counts.items()))


def check_value(key, value):
    """Value-level checks; returns a list of error messages."""
    errors = []

    key_placeholders = set(PLACEHOLDER_RE.findall(key))
    value_placeholders = set(PLACEHOLDER_RE.findall(value))
    if key_placeholders != value_placeholders:
        errors.append('placeholders do not match: key has %s, value has %s'
                      % (placeholder_text(key_placeholders),
                         placeholder_text(value_placeholders)))

    key_tags = tag_counts(key)
    value_tags = tag_counts(value)
    if key_tags != value_tags:
        errors.append('rich text tags do not match: key has %s, value has %s'
                      % (tag_text(key_tags), tag_text(value_tags)))

    for marker in URL_MARKERS:
        if marker in value and marker not in key:
            errors.append('contains "%s" (URLs are not allowed in translations)' % marker)

    bad = sorted({ch for ch in value
                  if unicodedata.category(ch) in ('Cc', 'Cs') and ch not in '\n\t'})
    if bad:
        shown = ', '.join('U+%04X' % ord(ch) for ch in bad[:3])
        if len(bad) > 3:
            shown += ' ... (%d kinds)' % len(bad)
        errors.append('contains control characters: %s' % shown)

    limit = 4 * len(key) + VALUE_LENGTH_SLACK
    if len(value) > limit:
        errors.append('too long: %d characters (limit %d for this key)' % (len(value), limit))

    return errors


def check_file(path_string, template_keys):
    """Check one translation file; returns a result dict."""
    result = {
        'path': path_string,
        'language': None,
        'name': None,
        'strings': {},
        'ok': False,
        'errors': [],
        'warnings': [],
        'translated': 0,
        'total': 0,
    }
    path = Path(path_string)
    errors = result['errors']
    warnings = result['warnings']

    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append('cannot read file: %s' % exc)
        return result
    if len(raw) > MAX_FILE_BYTES:
        errors.append('file is %d bytes, above the 2 MB limit (%d bytes)'
                      % (len(raw), MAX_FILE_BYTES))
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as exc:
        errors.append('file is not valid UTF-8: %s' % exc)
        return result
    try:
        data = json.loads(text)
    except ValueError as exc:
        errors.append('invalid JSON: %s' % exc)
        return result
    if not isinstance(data, dict):
        errors.append('top-level value must be a JSON object')
        return result

    language = data.get('language')
    if not isinstance(language, str):
        errors.append('"language" must be a string')
    else:
        result['language'] = language
        if not LANGUAGE_RE.match(language):
            errors.append('"language" %r does not match ^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$'
                          % language)
        elif language in RESERVED_LANGUAGES:
            errors.append('"language" %r is reserved (ja, en and zh are built in, '
                          'template is the template file)' % language)
        if language != path.stem:
            errors.append('"language" %r does not match the file name %r'
                          % (language, path.name))

    if 'name' not in data:
        errors.append('missing required field "name"')
    else:
        name = data['name']
        if not isinstance(name, str):
            errors.append('"name" must be a string')
        else:
            result['name'] = name
            if not 1 <= len(name) <= MAX_NAME_LENGTH:
                errors.append('"name" must be 1 to %d characters long, got %d'
                              % (MAX_NAME_LENGTH, len(name)))

    if 'authors' in data:
        authors = data['authors']
        if not isinstance(authors, list) or any(not isinstance(a, str) for a in authors):
            errors.append('"authors" must be an array of strings')

    if 'strings' not in data:
        errors.append('missing required field "strings"')
        strings = {}
    else:
        strings = data['strings']
        if not isinstance(strings, dict):
            errors.append('"strings" must be an object mapping source text to translations')
            strings = {}
        else:
            result['strings'] = {key: value for key, value in strings.items()
                                 if isinstance(value, str)}
    result['total'] = len(strings)

    for key, value in strings.items():
        if not isinstance(value, str):
            errors.append('strings[%r]: value must be a string' % preview(key))
            continue
        if template_keys is not None and key not in template_keys:
            warnings.append('strings[%r]: key is not in the template (old key?)' % preview(key))
        if not value:
            continue
        result['translated'] += 1
        for message in check_value(key, value):
            errors.append('strings[%r]: %s' % (preview(key), message))

    result['ok'] = not errors
    return result


def load_template(path_string):
    try:
        data = json.loads(Path(path_string).read_text(encoding='utf-8'))
        strings = data['strings']
        if not isinstance(strings, dict):
            raise TypeError('"strings" must be an object')
        return set(strings)
    except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as exc:
        print('check_translations.py: cannot load template %s: %s'
              % (path_string, exc), file=sys.stderr)
        raise SystemExit(2)


def coverage_markdown(results, template_keys):
    lines = ['# Translation coverage', '',
             '| Language | Name | Translated | Total | % |',
             '| --- | --- | ---: | ---: | ---: |']
    def sort_key(result):
        return result['language'] or Path(result['path']).stem
    for result in sorted(results, key=sort_key):
        language = result['language'] or Path(result['path']).stem
        name = (result['name'] or '-').replace('|', '\\|')
        if template_keys is None:
            translated = sum(1 for value in result['strings'].values() if value)
            total_text = '-'
            percent_text = '-'
        else:
            translated = sum(1 for key in template_keys if result['strings'].get(key))
            total_text = str(len(template_keys))
            percent_text = ('%.1f%%' % (100.0 * translated / len(template_keys))
                            if template_keys else '-')
        lines.append('| %s | %s | %d | %s | %s |'
                     % (language, name, translated, total_text, percent_text))
    lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        prog='check_translations.py',
        description='Check Dreamforge community translation files '
                    '(translations/<code>.json).')
    parser.add_argument('--template', metavar='PATH',
                        help='template.json; keys missing from it are reported '
                             'as warnings (old keys), not errors')
    parser.add_argument('--json', action='store_true',
                        help='write results as JSON to stdout')
    parser.add_argument('--coverage', metavar='OUT.md',
                        help='also write a per-language coverage table as '
                             'Markdown to OUT.md')
    parser.add_argument('files', nargs='+', metavar='FILE',
                        help='translation files to check '
                             '(a file named template.json is skipped)')
    args = parser.parse_args(argv)

    template_keys = load_template(args.template) if args.template else None

    files = []
    for path_string in args.files:
        if Path(path_string).name == 'template.json':
            print('skipping template file %s' % path_string, file=sys.stderr)
        else:
            files.append(path_string)

    results = [check_file(path_string, template_keys) for path_string in files]

    if args.coverage:
        Path(args.coverage).write_text(coverage_markdown(results, template_keys),
                                       encoding='utf-8')
        print('coverage table written to %s' % args.coverage, file=sys.stderr)

    if args.json:
        fields = ('path', 'language', 'ok', 'errors', 'warnings', 'translated', 'total')
        print(json.dumps({'files': [{field: result[field] for field in fields}
                                    for result in results]},
                         ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = 'ok' if result['ok'] else 'FAIL'
            print('%s: %s  (translated %d/%d, errors %d, warnings %d)'
                  % (result['path'], status, result['translated'], result['total'],
                     len(result['errors']), len(result['warnings'])))
            for message in result['errors']:
                print('  error: %s' % message)
            for message in result['warnings']:
                print('  warning: %s' % message)

    return 0 if all(result['ok'] for result in results) else 1


if __name__ == '__main__':
    sys.exit(main())
