import re
import json
import allure
import yaf.utils.regex_operations as regex
import yaf.utils.active_templates as act_tmpl
import yaf.utils.json_static_param as json_sp
import yaf.data.parsers.sql_command_extractor as sql_sp
from yaf.utils.json_static_param import is_payload_json


class Base:
    connections = None
    stash: dict = {}
    rqCounter: int = 0
    rsCounter: int = 0
    sqlRsCounter: int = 0

    @classmethod
    def reset(cls):
        cls.rqCounter = 0
        cls.rsCounter = 0
        cls.sqlRsCounter = 0
        cls.stash = {key: value for key, value
                     in cls.stash.items()
                     if key.startswith('global.')
                     or key.startswith('setup.once.before.')}

    @staticmethod
    def put_request_to_stash(body):
        Base.rqCounter += 1
        Base.stash[f'RQ_{Base.rqCounter}'] = body

    @staticmethod
    def put_response_to_stash(body):
        Base.rsCounter += 1
        Base.stash[f'RS_{Base.rsCounter}'] = body

    @staticmethod
    def put_sql_result_to_stash(sql_result):
        Base.sqlRsCounter += 1
        Base.stash[f'SQL_RS_{Base.sqlRsCounter}'] = sql_result

    @staticmethod
    def render_and_attach(raw_payload):
        rendered = Base.perform_replacement_and_return(text=raw_payload)
        rendered = rendered if isinstance(rendered, str) else str(rendered)
        allure.attach(rendered, 'rendered text - \n', allure.attachment_type.TEXT)
        return rendered

    @staticmethod
    def attach_block(body, info_mess, save: bool, is_request: bool):
        if body is not None:
            attach = allure.attachment_type.TEXT
            if is_payload_json(body):
                attach = allure.attachment_type.JSON
                body = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
            # TODO:: add later xml type
            # is_xml = is_payload_xml(body)
            allure.attach(body, info_mess, attach)
            if save:
                if is_request:
                    Base.put_request_to_stash(body)
                else:
                    Base.put_response_to_stash(body)

    @staticmethod
    def attach_request_block(body, info_mess, save: bool):
        Base.attach_block(body=body,
                          info_mess=info_mess,
                          save=save,
                          is_request=True)

    @staticmethod
    def attach_response_block(body, info_mess):
        Base.attach_block(body=body,
                          info_mess=info_mess,
                          save=True,
                          is_request=False)

    @staticmethod
    def perform_replacement_and_return(text):
        temp_text = text
        for deep in range(3):
            render_set = set(re.findall('({{ ((?:(?!{{ | }}).)+) }})', temp_text))
            for temp, inst in render_set:
                rendered = Base.render_template(inst, True)
                if rendered != inst:
                    if not isinstance(rendered, str) and temp == text:
                        return rendered
                    temp_text = temp_text.replace(temp, str(rendered))
            deep += 1
        return temp_text

    @staticmethod
    def render_template(raw_plate, is_hard_replaced: bool):
        answer = regex.get_base_path(template=raw_plate, connections=Base.connections)
        answer = json_sp.get_value_from_object_of_stash(query=answer, stash=Base.stash)
        answer = json_sp.get_header_value(query=answer, stash=Base.stash)
        answer = act_tmpl.get_object_from_stash(query=answer, stash=Base.stash)
        answer = act_tmpl.get_variable_from_stash(query=answer, stash=Base.stash)
        answer = act_tmpl.get_variable_from_env_file(query=answer)
        answer = act_tmpl.process_jinja_template(query=answer)
        answer = json_sp.get_resources_file(path=answer)
        answer = sql_sp.get_value_from_stash(text=answer, stash=Base.stash)
        if is_hard_replaced:
            answer = regex.generate_by_regex(template=answer)
            if answer == raw_plate:
                answer = json_sp.get_from_test_data(key=answer, stash=Base.stash)
        return answer
