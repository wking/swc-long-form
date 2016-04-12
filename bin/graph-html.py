#!/usr/bin/env python3
#
# -*- coding: <encoding name> -*-

import csv
import os.path
import sys


PAGE_TEMPLATE = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8"/>
  </head>
  <body>
    <h1>{name}</h1>
    <h2>Parents</h2>
    {parent_tree}
    <h2>Children</h2>
    {child_tree}
  </body>
</html>
'''


class Node(object):
    page_template = PAGE_TEMPLATE

    def __init__(self, id, name, parents=None, children=None):
        self.id = id
        self.name = name
        if parents is None:
            parents = []
        self.parents = parents
        if children is None:
            children = []
        self.children = children

    def __unicode__(self):
        return '<Node {}>'.format(self.name)

    def __repr__(self):
        return '<Node {}>'.format(self.name)

    def generate_html(self):
        path = os.path.join('html', '{}.html'.format(self.id))
        parent_tree = self._tree_html(attribute='parents')
        child_tree = self._tree_html(attribute='children')
        with open(path, 'w') as f:
            f.write(self.page_template.format(
                parent_tree=parent_tree,
                child_tree=child_tree,
                **self.__dict__)
            )

    def _tree_html(self, attribute, depth=0):
        lines = []
        nodes = getattr(self, attribute)
        if nodes:
            lines.append('<ul>')
            if depth > 1:
                lines.append('<li>…</li>')
            else:
                for node in nodes:
                    lines.append('<li>')
                    lines.append(
                        '<a href="{}.html">{}</a>'.format(node.id, node.name))
                    recursive = node._tree_html(
                        attribute=attribute,
                        depth=depth + 1)
                    if recursive:
                        lines.append(recursive)
                    lines.append('</li>')
            lines.append('</ul>')
        return '\n'.join(lines)


def read_graph(stream=sys.stdin):
    reader = csv.DictReader(stream)
    index = Node(id='index', name='Design')
    nodes = {'index': index}
    for row in reader:
        if row['type'] == 'node':
            node = Node(
                id=row['ident'],
                name='{}: {}'.format(row['subtype'], row['value'])
            )
            nodes[row['ident']] = node
            if row['subtype'] == 'question':
                index.children.append(node)
                node.parents.append(index)
        elif row['type'] == 'link':
            parent = nodes[row['ident']]
            child = nodes[row['value']]
            parent.children.append(child)
            child.parents.append(parent)
        else:
            raise NotImplementedError(
                'unrecognized row type: {!r}'.format(row['type']))
    return nodes


def main(stream=sys.stdin):
    graph = read_graph(stream=stream)
    for node in graph.values():
        node.generate_html()


if __name__ == '__main__':
    main()
