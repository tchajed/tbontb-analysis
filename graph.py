#!/usr/bin/env python3

import bs4.element
from bs4 import BeautifulSoup
from graphviz import Digraph
from os.path import join, basename, splitext

BOOK_DIR = "tbontb"


class Link:
    def __init__(self, text, src, dst, implicit=False):
        self.text = text
        self.src = src
        self.dst = dst
        self.implicit = implicit

    @classmethod
    def implicit(cls, src, dst):
        return cls("", src, dst, implicit=True)

    @property
    def is_shakespeare(self):
        return "☠" in self.text

    @property
    def is_restart(self):
        return self.text == "» Restart? «"


class Page:
    def __init__(self, name, soup):
        self.name = name
        self._body = soup.find("body")

    @classmethod
    def from_file(cls, fname):
        with open(join(BOOK_DIR, fname)) as f:
            soup = BeautifulSoup(f, "html.parser")
            return cls(fname, soup)

    @property
    def title(self):
        return self._soup.head.title.text

    @property
    def image(self):
        """Filename of the main image on the page.

        None if there is no image on the page.
        """
        img = self._body.find("img")
        if img is None:
            return None
        return img["src"]

    @property
    def ending_image(self):
        img = self._body.select_one("img.fullscreen")
        if img is None:
            return None
        return img["src"]

    @property
    def is_ending(self):
        # judge endings by presence of a single fullscreen image
        imgs = self._body.select("img.fullscreen")
        if len(imgs) == 1:
            return True
        else:
            return False


    def choices(self):
        """List of Links found on the page"""
        src = self.name
        links = []
        for a_tag in self._body.select(".choice a"):
            dst = a_tag["href"]
            link = Link(a_tag.text, src, dst)
            links.append(link)
        return links


class Chapter:
    def __init__(self, navPoint):
        self._tag = navPoint

    @property
    def order(self):
        return int(self._tag["playOrder"])

    @property
    def label(self):
        return self._tag.navLabel.text

    @property
    def content_file(self):
        """File name of chapter contents."""
        return self._tag.content["src"]

    def page(self):
        return Page.from_file(self.content_file)


class Node:
    def __init__(self, chapter, next_chapter):
        self.chapter = chapter
        page = chapter.page()
        links = page.choices()
        if not links and next_chapter and not page.is_ending:
            links = [Link.implicit(chapter.content_file,
                next_chapter.content_file)]

        self.page = page
        self.links = links

    @property
    def content_file(self):
        return self.chapter.content_file

    @property
    def ident(self):
        """Return a unique identifier, based on filename."""
        name, ext = splitext(basename(self.content_file))
        return name

    @property
    def label(self):
        return self.chapter.label

    @property
    def is_ending(self):
        return self.page.is_ending

    @property
    def ending_image(self):
        return self.page.ending_image


with open(join(BOOK_DIR, "book.ncx")) as f:
    soup = BeautifulSoup(f, "xml")


chapters = [Chapter(navPoint) for navPoint in soup.ncx.find_all("navPoint")]
chapters.sort(key=lambda c: c.order)

nodes = []
for i, chapter in enumerate(chapters):
    if i == len(chapters) - 1:
        next_chapter = None
    else:
        next_chapter = chapters[i+1]
    node = Node(chapter, next_chapter)
    nodes.append(node)

dot = Digraph(name="To Be Or Not To Be")

for node in nodes:
    attrs = {"href": join(BOOK_DIR, node.content_file),
            "id": node.ident}
    if node.is_ending:
        height = 7.0
        attrs.update({
            "color": "purple",
            "image": join(BOOK_DIR, node.ending_image),
            "fixedsize": "true",
            "imagescale": "true",
            "shape": "box",
            "height": str(height+0.5),
            "width": str(height/1.5),
            "labelloc": "b",
            })
    dot.node(node.content_file, node.label, **attrs)
    for link in node.links:
        # Not only are these unnecessary, rendering is about 20x faster without
        # them due to layout
        if link.is_restart:
            continue
        attrs = {}
        if link.implicit:
            attrs["color"] = "gray"
        if link.is_shakespeare:
            attrs["color"] = "red"
        dot.edge(link.src, link.dst, **attrs)

dot.save("tbontb.dot")
