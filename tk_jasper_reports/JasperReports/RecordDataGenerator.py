# coding=utf-8
# #############################################################################
#
# Copyright (c) 2008-2012 NaN Projectes de Programari Lliure, S.L.
#                         http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import csv
from xml.dom.minidom import getDOMImplementation
import codecs

from JasperReport import *
from AbstractDataGenerator import *


class CsvRecordDataGenerator(AbstractDataGenerator):
    def __init__(self, report, data):
        self.temporaryFiles = []
        self.data = data
        self.report = report

    # CSV file generation using a list of dictionaries provided by the parser function.
    def generate(self, fileName):
        f = open(fileName, 'wb+')
        csv.QUOTE_ALL = True
        fieldNames = self.report.fieldNames()
        # JasperReports CSV reader requires an extra colon at the end of the line.
        writer = csv.DictWriter(f, fieldNames + [''], delimiter=',', quotechar='"')
        header = {}
        for field in fieldNames + ['']:
            header[field] = field
        writer.writerow(header)
        for record in self.data['records']:
            row = {}
            for field in record:
                if field not in self.report.fields():
                    print "FIELD '%s' NOT FOUND IN REPORT." % field
                    continue
                value = record.get(field, False)
                if not value:
                    value = ''
                elif isinstance(value, unicode):
                    value = value.encode('utf-8')
                elif not isinstance(value, str):
                    value = str(value)
                row[self.report.fields()[field]['name']] = value
            writer.writerow(row)
        f.close()


class XmlRecordDataGenerator(AbstractDataGenerator):
    def __init__(self, report, data):
        self.temporaryFiles = []
        self.data = data
        self.report = report

    def handle_list_values(self, document, topNode, field_name, values):
        for record in values:
            recordNode = document.createElement(field_name)
            topNode.appendChild(recordNode)
            for field, value in record.iteritems():
                if type(value) == type([]):
                    self.handle_list_values(document, recordNode, field, value)
                    continue

                fieldNode = document.createElement(field)
                recordNode.appendChild(fieldNode)

                # The rest of field types must be converted into str
                if not value:
                    value = ''
                elif isinstance(value, str):
                    value = unicode(value, 'utf-8')
                elif not isinstance(value, unicode):
                    value = unicode(value)
                valueNode = document.createTextNode(value)
                fieldNode.appendChild(valueNode)

    # XML file generation using a list of dictionaries provided by the parser function.
    def generate(self, fileName):
        # Once all records have been calculated, create the XML structure itself
        self.document = getDOMImplementation().createDocument(None, 'data', None)
        topNode = self.document.documentElement
        for record in self.data['records']:
            recordNode = self.document.createElement('record')
            topNode.appendChild(recordNode)
            for field, value in record.iteritems():
                # if field not in self.report.fields():
                # print "FIELD '%s' NOT FOUND IN REPORT." % field
                # continue

                if type(value) == type([]):
                    self.handle_list_values(self.document, recordNode, field, value)
                    continue

                fieldNode = self.document.createElement(field)
                recordNode.appendChild(fieldNode)
                # The rest of field types must be converted into str
                if not value:
                    value = ''
                elif isinstance(value, str):
                    value = unicode(value, 'utf-8')
                elif not isinstance(value, unicode):
                    value = unicode(value)
                valueNode = self.document.createTextNode(value)
                fieldNode.appendChild(valueNode)
        # Once created, the only missing step is to store the XML into a file
        f = codecs.open(fileName, 'wb+', 'utf-8')
        topNode.writexml(f)
        f.close()
