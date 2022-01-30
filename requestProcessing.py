import json
import threading
import logging
import re


class RequestProcessing:

    format = "%(asctime)s: %(message)s"
    model_keys = {"path", "method", "query_params", "headers", "body"}
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    global models

    """
    This function simulates getting of a new request and processing the request
    I'm processing the requests n parallel by using multi threading
    """
    def run(self):

        models = RequestProcessing.load_jsonfile("models.json")  # Load the models
        requests = RequestProcessing.load_jsonfile("requests.json")  # Load the Requests

        threads = list()  # Processing the requests in parallel
        for index in range(len(requests)):
            logging.info("Main: create and start thread %d.", index)
            x = threading.Thread(target=RequestProcessing.valid_request(requests[index], models), args=(index,))
            threads.append(x)
            x.start()

    """
    The purpose of that function is to find what is the type of the string
    :param str - s some value from the request
    :return - type of the value
    """
    @staticmethod
    def get_str_type(value):
        if len(str(value)) == 0:
            return None
        if isinstance(value, list):
            return "List"
        if str(value).lower() == 'false' or str(value).lower() == 'true':
            return "Boolean"
        if re.match(r'^[0-9a-zA-z]+-[0-9a-zA-z]+-[0-9a-zA-z]+-[0-9a-zA-z]+$', str(value)) is not None:
            return "UUID"
        if re.match(r'^[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]$', str(value)) is not None:
            return "Date"
        if re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', str(value)) is not None:
            return "Email"
        if re.match(r'^Bearer [a-zA-Z0-9]+$', str(value)) is not None:
            return "Auth-Token"
        if re.match(r'^[0-9]+$', str(value)) is not None:
            if str(value)[0] == '0':
                return 'String'
            else:
                return "Int"
        return "String"

    """
    Check if the value of the request is valid, also check if the type of the request is ok
    :param value - value of the name
    :param types - the types that the model agree to get
    :param query_params - the params of single request 
    :return abnormal dictionary 
    """
    @staticmethod
    def validate_query_params(query_request, query_model):
        valid = False  # Used for param request validation
        abnormal = {}
        for param_request in query_request:
            name = param_request["name"]
            value_type = RequestProcessing.get_str_type(param_request["value"])
            for param_model in query_model:
                if param_model["name"] == name and value_type in param_model["types"]:
                    valid = True
                    break
            if not valid:  # Used to fetch the wrong types
                for param_model in query_model:
                    if param_model["name"] == name:
                        abnormal[name] = {"got": value_type, "expected": param_model["types"]}
            valid = False

        valid = False

        for param_model in query_model:
            required = param_model["required"]
            if str(required) == "true":
                name = param_model["name"]
                for param_request in query_request:
                    if param_request["name"] == name:
                        valid = True
                        break
                if not valid:
                    for request_name in param_request:
                        if name == request_name["name"]:
                            abnormal[name] = "{} is required".format(name)
                            break
                valid = False
        return abnormal

    """
    This function checks if the there any abnormal fields in the query_params, headers and body
    :param request - a single request to check
    :param model - a model with the same path and method that we have in the request
    :return result - dictionary with the abnormal fields, if the fields are ok then the result is empty 
    """
    @staticmethod
    def compare_query_param(request, model):
        result = {}
        query_params = RequestProcessing.validate_query_params(request["query_params"], model["query_params"])
        headers = RequestProcessing.validate_query_params(request["headers"], model["headers"])
        body = RequestProcessing.validate_query_params(request["body"], model["body"])

        if bool(query_params):
            result["query_params"] = query_params
        if bool(headers):
            result["headers"] = headers
        if bool(query_params):
            result["body"] = body
        return result

    """
    The purpose of valid_request function is to check the validation of the request
    In any case the function will print 200 ok with a json that describes the issues that the function found
    :param request - a single request
    :param models - a dictionary with the all models
    :return None
    """
    @staticmethod
    def valid_request(request, models):
        # Check if the request is empty
        if not request:
            logging.error('"200 OK": "abnormal", "reason": "the request is empty"')
            return
        # Check the keys structure of the request
        for key in request.keys():
            if key not in RequestProcessing.model_keys:
                logging.error('"200 OK": "abnormal", "reason": "one or more of the keys in the request missing"')
                return

        # Get the model with the same path like the request
        for ml in models:
            if ml["path"] == request["path"] and ml["method"] == request["method"]:
                model = ml
                break

        # if the model is none then the request does not similar to any model
        if model is None:
            logging.error('"200 OK": "abnormal", "reason": "no path of method like the model"')
            return

        request_result = RequestProcessing.compare_query_param(request, model)
        if not request_result:
            logging.info('{"200 OK": "valid"}')
        else:
            request_result["200 OK"] = "abnormal"
            logging.info(request_result)

    """
    Load a json file to variable 
    :param json_path_file - path of the json file
    :return dictionary of the json
    """
    @staticmethod
    def load_jsonfile(json_path_file):
        # Opening JSON file
        f = open(json_path_file)
        # returns JSON object a dictionary
        data = json.load(f)
        f.close()
        return data


if __name__ == '__main__':
    start = RequestProcessing()
    start.run()


