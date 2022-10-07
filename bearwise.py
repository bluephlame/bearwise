import os
import sys

import xcall
import datetime
import requests
import json
from datetime import datetime
from jinja2 import Environment, Template, select_autoescape

env = Environment(
    autoescape=select_autoescape()
)


def fetch_from_export_api(updated_after=None):
    full_data = []
    next_page_cursor = None
    while True:
        params = {}
        if next_page_cursor:
            params['pageCursor'] = next_page_cursor
        if updated_after:
            params['updatedAfter'] = updated_after
        print("Making export api request with params " + str(params) + "...")
        response = requests.get(
            url="https://readwise.io/api/v2/export/",
            params=params,
            headers={"Authorization": f"Token {token}"}, verify=True
        )
        full_data.extend(response.json()['results'])
        next_page_cursor = response.json().get('nextPageCursor')
        if not next_page_cursor:
            break
    return full_data


def open_book_note(book: object):
    try:
        result = xcall.xcall('bear', 'open-note',
                {'title': book['readable_title'],
                 'header': "ID:{}".format(book['user_book_id']),
                 'exclude_trashed': 'yes'
                 })
        return result['identifier']
    except xcall.XCallbackError:
        return False


def create_book_note(book: object):
    with open('book.md') as f:
        template = Template(f.read())
        render_output = template.render(book)
        result = xcall.xcall('bear','create',
                    {'text':render_output, 'show_window':'no'})
        # Future feature: add in url to link in the book cover. and use cover_image_url from readwise.
    return result['identifier']


def append_highlight(highlight: object, note_id: str):
    result = xcall.xcall('bear', 'open-note',
                         {'id': note_id})
    in_note = result['note'].find(str(highlight['id']))

    if in_note < 0:
        with open('highlight.md') as f:
            template = Template(f.read())
            render_output = template.render(highlight)
            result = xcall.xcall('bear', 'add-text',
                        {'id': note_id, 'header': 'Highlights',
                         'text': render_output, 'show_window': 'no'})
    return result


def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable),path))

        # resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path


if __name__ == '__main__':
    with open(resolve_path('config.json')) as file:
        data = json.load(file)

    global token
    token = data['token']

    if 'last_fetch_date' in data:
        print('Processing readwise Highlights since {}'.format(data['last_fetch_date']))
        all_data = fetch_from_export_api(data['last_fetch_date'])
    else:

        print('Processing readwise Highlights since epoc')
        all_data = fetch_from_export_api()

    print('There are {} new highlights'.format(len(all_data)))
    for book in all_data:
        note_id = open_book_note(book)
        if not note_id:
            note_id = create_book_note(book)
        for highlight in book['highlights']:
            append_highlight(highlight, note_id)
    data['last_fetch_date'] = datetime.now().isoformat()
    with open(resolve_path('config.json'), 'w') as outfile:
        json.dump(data, outfile)

