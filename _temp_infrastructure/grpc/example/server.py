import grpc
import logging
from concurrent.futures import ThreadPoolExecutor
from google.protobuf import wrappers_pb2 as wrappers

protos, services = grpc.protos_and_services("example.proto")

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(name)21s :: %(funcName)16s() :: %(message)s')
handler.setFormatter(formatter)


class ComplianceCheckServiceDispatcher(services.ComplianceCheckServiceServicer):
    log = logging.getLogger('ComplianceCheckService')
    log.setLevel(logging.INFO)
    log.addHandler(handler)

    def CheckOperation(self, request, context):
        ComplianceCheckServiceDispatcher.log.info(f'get request...\n{request.operation.class_code.value}')
        kwargs = {
            'status': protos.CheckStatus.ALLOWED,
            'error_code': protos.ErrorCode.BLOCKED_BY_NEED_SURVEY_PASSED,
            'error_message': wrappers.StringValue(value='Ошибок нет')
        }
        return protos.CheckResult(**kwargs)


class ComplianceLoadServiceDispatcher(services.ComplianceLoadServiceServicer):
    log = logging.getLogger('ComplianceLoadService')
    log.setLevel(logging.INFO)
    log.addHandler(handler)

    def LoadSanctionItems(self, request, context):
        ComplianceLoadServiceDispatcher.log.info(f'get Compliance Load Service request...\n{str(request.items)}')
        return wrappers.BoolValue(value=True)


if __name__ == '__main__':
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    services.add_ComplianceCheckServiceServicer_to_server(ComplianceCheckServiceDispatcher(), server)
    services.add_ComplianceLoadServiceServicer_to_server(ComplianceLoadServiceDispatcher(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
