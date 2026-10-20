#!/usr/bin/env python3
"""Clear the page cache (WP Super Cache) so visitors see changes at once. Called by the other tools after they change the site;
run it by hand after any other change (page edits, snippets, global styles, footer, settings)."""
import json, subprocess
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp-super-cache/v1/cache'


def clear():
    out = subprocess.run(['curl', '-sS', '-X', 'POST', W, '-H', 'Content-Type: application/json', '-d', '{}'], capture_output=True).stdout
    try:
        return json.loads(out).get('Cache Cleared', False)
    except ValueError:
        return False


if __name__ == '__main__':
    print('page cache cleared:', clear())
