#!/usr/bin/env python3

import bs4.element
from bs4 import BeautifulSoup
from graphviz import Digraph
from os.path import join, basename, splitext




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
    def from_file(cls, fname, name):
        with open(fname) as f:
            soup = BeautifulSoup(f, "html.parser")
            return cls(name, soup)

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
        if self._body.findAll(text="THE END"):
            return True
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
    def __init__(self, content_dir, navPoint):
        self._dir = content_dir
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
        return Page.from_file(join(self._dir, self.content_file), self.content_file)


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


def read_nodes(content_dir):
    with open(join(content_dir, "book.ncx")) as f:
        soup = BeautifulSoup(f, "xml")

    chapters = [Chapter(content_dir, navPoint) for navPoint in soup.ncx.find_all("navPoint")]
    chapters.sort(key=lambda c: c.order)

    nodes = []
    for i, chapter in enumerate(chapters):
        if i == len(chapters) - 1:
            next_chapter = None
        else:
            next_chapter = chapters[i+1]
        node = Node(chapter, next_chapter)
        nodes.append(node)

    return nodes


def node_graph(content_dir, nodes):
    dot = Digraph(name="To Be Or Not To Be",
            graph_attr={"id": "viewport"})
    for node in nodes:
        attrs = {"href": join(content_dir, node.content_file),
                "id": node.ident}
        if node.is_ending:
            attrs.update({
                "color": "purple",
                "shape": "box",
                })
            if node.ending_image:
                height = 7.0
                attrs.update({
                    "image": join(content_dir, node.ending_image),
                    "fixedsize": "true",
                    "imagescale": "true",
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
    return dot


if __name__ == "__main__":
    book_dir = "tbontb"
    nodes = read_nodes(book_dir)
    dot = node_graph(book_dir, nodes)
    dot.save("tbontb.dot")
