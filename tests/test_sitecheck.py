from cfadvisers import sitecheck


def test_analyse_finds_team_contact_email():
    html = """<a href="/about">About</a><a href="/our-people/">Our People</a><a href="https://x.co.uk/contact-us">Contact</a>
    <a href="mailto:jo.bloggs@x.co.uk">Jo</a> enquiries@x.co.uk tracking@sentry.io <a href="tel:+44 113 000 0000">call</a>
    <a href="https://twitter.com/team">Team on Twitter</a> <a href="mailto:">blank</a> <a href="mailto:%20">x</a>"""
    got = sitecheck.analyse("https://www.x.co.uk/", html)
    assert got["team_url"] == "https://www.x.co.uk/our-people/"
    assert got["contact_url"] == "https://x.co.uk/contact-us" or got["contact_url"] is None
    assert got["best_email"] == "enquiries@x.co.uk"
    assert got["phone"] == "+44 113 000 0000"


def test_root_domain():
    assert sitecheck.root_domain("www.foo.co.uk") == "foo.co.uk"
    assert sitecheck.root_domain("mail.foo.com") == "foo.com"
