# -*- coding: utf-8 -*-
"""
--------------------------------------------------
    Date Time ：     2023/10/13 17:18
    Author ：        dokeyhou
    IDE ：           PyCharm
    File ：          wsdl_parser.py
    Description:
--------------------------------------------------
"""

import argparse
from typing import Union

import requests
from lxml import etree


class ServiceMethod:
    """
  服务方法定义。

  Args:
    method_name: 服务方法名称。
    input_params: 请求参数定义。
    output_params: 输出参数定义。
  """

    def __init__(self, method_name: str, input_params: dict, output_params: dict):
        self.method_name = method_name
        self.input_params = input_params
        self.output_params = output_params


class ParamType(object):
    name: str
    type: str
    minOccurs: int
    maxOccurs: int
    nillable: bool
    tns: str


class ComplexParamType(ParamType):
    attrs: list[ParamType]


class MessageType(object):
    name: str


class MessagePartType(MessageType):
    paramType: ParamType | ComplexParamType | None


class WSDLParser(object):
    wsdl_url: str
    root_xml: etree._Element
    param_types: dict[str, list[ParamType | ComplexParamType]]
    message_types: list[ParamType | ComplexParamType]

    def __init__(self, wsdl_url: str = None):
        self.wsdl_url = wsdl_url

    def feed(self, content: bytes = None, encoding="utf-8"):
        xml_parser = None
        if encoding:
            xml_parser = etree.XMLParser(encoding=encoding)
        if content:
            self.root_xml = etree.fromstring(content, xml_parser)
        else:
            resp = requests.get(self.wsdl_url)
            self.root_xml = etree.fromstring(resp.content, xml_parser if xml_parser else etree.XMLParser(resp.encoding))

    def get_prefix(self, root: etree._Element = None) -> str:
        if root is None:
            root = self.root_xml
        prefix = ""
        if root.prefix and root.prefix != "":
            prefix = f"{{{root.nsmap[root.prefix]}}}"
        return prefix

    def get_tags(self, tag: str, root: etree._Element = None) -> list[etree._Element]:
        if root is None:
            root = self.root_xml
        elements = root.findall(f"{self.get_prefix(root)}{tag}")
        return elements

    def get_services(self) -> list[etree._Element]:
        return self.get_tags("service")

    def get_port_types(self) -> list[etree._Element]:
        return self.get_tags("portType")

    def get_messages(self) -> list[etree._Element]:
        return self.get_tags("message")

    def get_bindings(self) -> list[etree._Element]:
        return self.get_tags("binding")

    def get_types(self) -> etree._Element:
        types = self.root_xml.find(f"{self.get_prefix()}types")
        return types

    def parse_element(self, element: etree._Element) -> Union[ParamType, ComplexParamType, None]:
        if element is None:
            return None
        param = ParamType()
        param.name = element.attrib["name"]
        param.targetNamespace = element.nsmap["targetNamespace"]
        type = element.attrib["type"]
        if type:
            param.type = type.removeprefix(f"{element.prefix}:")
            # parse extend attrs
            param.minOccurs = int(element.attrib["minOccurs"]) if element.attrib["minOccurs"] else None
            param.maxOccurs = int(element.attrib["maxOccurs"]) if element.attrib["maxOccurs"] else None
            param.nillable = bool(element.attrib["nillable"]) if element.attrib["nillable"] else False
            return param
        else:
            complexType = element.find(f"{self.get_prefix(element)}complexType")
            if complexType:
                param = ComplexParamType()
                param.name = element.attrib["name"]
                param.type = "complex"
                sequence = complexType.find(f"{self.get_prefix(complexType)}sequence")
                if sequence:
                    elements = self.get_tags("element", sequence)
                    param.attrs = []
                    for element in elements:
                        sub_param = self.parse_element(element)
                        param.attrs.append(sub_param)
                return param
            else:
                return param

    def parse_types(self) -> None:
        types = self.get_types()
        type_schemas = self.get_tags("schema", types)
        self.param_types = {}
        for schema in type_schemas:
            self.param_types[schema.attrib["targetNamespace"]] = []
            elements = self.get_tags("element", schema)
            for element in elements:
                param = self.parse_element(element)
                param.tns = schema.attrib["targetNamespace"]
                if param.type and param.type == "complex":
                    for attr in param.attrs:
                        attr.tns = param.tns
                self.param_types[schema.attrib["targetNamespace"]].append(param)

    def search_param_type(self, name: str, tns: str, ) -> ParamType | ComplexParamType | None:
        if tns and tns.strip() != "":
            params = self.param_types[tns.strip()]
            for param in params:
                searched_param = self._search_param_from_complex(param, name)
                if searched_param is not None:
                    return searched_param
        else:
            for _, params in enumerate(self.param_types):
                for param in params:
                    searched_param = self._search_param_from_complex(param, name)
                    if searched_param is not None:
                        return searched_param

    @staticmethod
    def _search_param_from_complex(self, param: ParamType | ComplexParamType,
                                   name: str) -> ParamType | ComplexParamType | None:
        if param is None:
            return None
        if param.name == name:
            return param
        elif param.type == "complex":
            for attr in param.attrs:
                result = self._search_param_from_complex(attr, name)
                if result is not None:
                    return result

    def parse_messages(self):
        messages = self.get_messages()
        for message in messages:
            parts = self.get_tags("part", message)
            for part in parts:
                part_type = MessagePartType()
                part_type.name = part.attrib["name"]
                element_ref = str(part.attrib["element"])
                index = element_ref.index(":")
                tns = ""
                param_name = element_ref
                if index > 0:
                    tns = element_ref[0:index]
                    param_name = element_ref[index + 1:]
                part_type.paramType = self.search_param_type(param_name, tns)

    def parse(self):
        self.feed()
        self.parse_types()
        self.parse_messages()


def generate_class(service_methods: list) -> None:
    """
  生成服务方法的 Python3 class 定义。

  Args:
    service_methods: 服务方法元数据。
  """

    for service_method in service_methods:
        print("class {}(ComplexType):".format(service_method.method_name))
        print("  def __init__(self, **kwargs):".format(service_method.method_name))
        print("    super().__init__(**kwargs)".format(service_method.method_name))
        for input_param in service_method.input_params:
            print("    self.{} = kwargs.get('{}', None)".format(input_param["name"], input_param["name"]))
        for output_param in service_method.output_params:
            print("  @property")
            print("  def {}(self):".format(output_param["name"]))
            print("    return self._{}.value".format(output_param["name"]))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="WSDL 解析器")
    parser.add_argument("-u", "--url", dest="url", type=str, required=True, help="WSDL 服务的 URL")
    args = parser.parse_args()

    wsdl_parser = WSDLParser(args.url)
    wsdl_parser.parse()


if __name__ == "__main__":
    # -u https://www.w3schools.com/xml/tempconvert.asmx?wsdl
    main()
