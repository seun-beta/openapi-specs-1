import copy
import json
import yaml

from re import sub

_PaginatedResourceWithNameURL = """{
    "200": {
        "description": "successful operation",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/PaginatedResourceWithNameURL"
                }
            }
        }
    }
}"""

_PaginatedResourceWithURL = """{
    "200": {
        "description": "successful operation",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/PaginatedResourceWithURL"
                }
            }
        }
    }
}"""

_parameters = """[
        {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
                "type": "integer",
                "default": 20
            }
        },
        {
            "name": "offset",
            "in": "query",
            "required": false,
            "schema": {
                "type": "integer",
                "default": 0
            }
        }
    ]"""

_schemas = """{
	"PaginatedResourceWithNameURL": {
		"type": "object",
		"properties": {
			"count": {
				"type": "integer"
			},
			"next": {
				"type": "string"
			},
			"previous": {
				"type": "string"
			},
			"results": {
				"type": "array",
				"items": {
					"type": "object",
					"properties": {
						"name": {
							"type": "string"
						},
						"url": {
							"type": "string"
						}
					}
				}
			}
		}
	},
	"PaginatedResourceWithURL": {
		"type": "object",
		"properties": {
			"count": {
				"type": "integer"
			},
			"next": {
				"type": "string"
			},
			"previous": {
				"type": "string"
			},
			"results": {
				"type": "array",
				"items": {
					"type": "object",
					"properties": {
						"url": {
							"type": "string"
						}
					}
				}
			}
		}
	}
}"""


def camel_case(s):
    return sub(r"(_|-|/)+", " ", s).title().replace(" ", "")


def _getListOperationId(path, method):
    return f"{method.lower()}{camel_case(path)}List"


if __name__ == '__main__':
    with open("pokeapi.yaml", 'r') as f:
        api_spec = yaml.safe_load(f.read())
        modified_spec = copy.deepcopy(api_spec)
        modified_spec['components']['schemas'].update(json.loads(_schemas))
        for path, path_data in api_spec['paths'].items():
            for resource_path in ["{id_or_name}/", "{id}/"]:
                if resource_path in path:
                    list_path = path.split(resource_path)[0]
                    print(f"{list_path}")
                    list_path_data = copy.deepcopy(path_data)
                    for method in list_path_data:
                        list_path_data[method]["operationId"] = _getListOperationId(list_path, method)
                        list_path_data[method]["summary"] = list_path_data[method]['summary'] + " List"
                        list_path_data[method]["description"] = "List for all " + list_path_data[method]["description"]
                        list_path_data[method]["parameters"] = json.loads(_parameters)
                        if resource_path == "{id_or_name}/":
                            list_path_data[method]["responses"] = json.loads(_PaginatedResourceWithNameURL)
                        else:
                            list_path_data[method]["responses"] = json.loads(_PaginatedResourceWithURL)
                        modified_spec['paths'][list_path] = list_path_data
    with open("modified_pokeapi.yaml", "w") as f:
        f.write(yaml.dump(modified_spec, sort_keys=False))
