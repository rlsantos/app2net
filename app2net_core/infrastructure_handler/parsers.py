from xml.etree import ElementTree
import datetime


# Parser deve utilizar VXDL puro ou a extensão que o Aurora utiliza? (ex: tag controllerList)
# Implementar todas as tags vxdl? (ex: software list)

class VxdlParser:
    def __init__(self):
        self.file = None

    @staticmethod
    def parse(file):
        raise NotImplementedError


class VxdlXmlParser(VxdlParser):
    @classmethod
    def parse(cls, file):
        virtual_infrastructure = {}

        et = ElementTree.parse(file)
        root = et.getroot()

        virtual_infrastructure["id"] = root.attrib["id"]
        virtual_infrastructure["owner"] = root.attrib["owner"]
        virtual_infrastructure["start_date"] = datetime.datetime.fromisoformat(
            root.find("startDate").text)

        nodes = root.findall("vNode")
        links = root.findall("vLink")

        virtual_infrastructure["nodes"] = [cls._parse_node(node) for node in nodes]
        virtual_infrastructure["links"] = [cls._parse_link(link) for link in links]

        return virtual_infrastructure

    @classmethod
    def _parse_node(cls, node_element: ElementTree.Element):
        cpu_node = node_element.find("cpu")
        cpu = {
            "cores": cpu_node.find("cores/simple").text,
            "frequency": cls._parse_resource_parameter(cpu_node.find("frequency"))
        }

        memory_node = node_element.find("memory")
        memory = cls._parse_resource_parameter(memory_node)

        storage_node = node_element.find("storage")
        storage = cls._parse_resource_parameter(storage_node)

        interface_nodes = node_element.findall("interface")
        interfaces = []

        for interface_node in interface_nodes:
            interfaces.append({
                "alias": interface_node.find("alias").text,
                "type": interface_node.find("type").text
            })

        software_nodes = node_element.findall("software_list/software")

        if software_nodes:
            software_list = [
                {"name": software.find("name").text,
                 "version": software.find("version").text}
                for software in software_nodes
            ]
        else:
            software_list = []

        return {
            "id": node_element.get("id"),
            "cpu": cpu,
            "memory": memory,
            "storage": storage,
            "image": node_element.findtext("image"),
            "interfaces": interfaces,
            "software_list": software_list
        }

    @staticmethod
    def _parse_resource_parameter(parameter_node):
        parameter = {}
        if parameter_node.find("interval"):
            parameter.update({
                "min": parameter_node.findtext("interval/min"),
                "max": parameter_node.findtext("interval/max"),
            })
        else:
            parameter.update({
                "value": parameter_node.findtext("simple")
            })

        parameter["unit"] = parameter_node.find("unit").text

        return parameter

    @classmethod
    def _parse_link(cls, link_node):
        bandwidth_node = link_node.find("bandwidth")
        bandwidth = {
            "forward": cls._parse_resource_parameter(bandwidth_node.find("forward")),
            "reverse": cls._parse_resource_parameter(bandwidth_node.find("reverse")),
        }

        latency_node = link_node.find("latency")
        latency = cls._parse_resource_parameter(latency_node)

        source = {
            "node": link_node.findtext("source/vNode"),
            "interface": link_node.findtext("source/interface"),
        }

        destination = {
            "node": link_node.findtext("destination/vNode"),
            "interface": link_node.findtext("destination/interface"),
        }

        return {
            "id": link_node.get("id"),
            "bandwidth": bandwidth,
            "latency": latency,
            "source": source,
            "destination": destination,
        }


if __name__ == "__main__":
    with open("vxdl_cnsm_tree_7.xml") as vxdl_file:
        v = VxdlXmlParser.parse(vxdl_file)
        import pprint
        pprint.pp(v)
