class Trace(Resource):

    def Log(api_name, trace_id, status, message, request_json, response_json):
        v_request_json = request_json.replace("\'", '\"').replace('None', 'null').replace('True', 'true').replace(
            'False', 'false')
        v_response_json = response_json.replace("\'", '\"').replace('None', 'null').replace('True', 'true').replace(
            'False', 'false')
        query = "call public.log_trace (:p_api_name, :p_trace_id, :p_status, :p_message, :p_request_json, " \
                ":p_response_json); commit; "
        params = {"p_api_name": api_name, "p_trace_id": trace_id, "p_status": status, "p_message": message,
                  "p_request_json": v_request_json, "p_response_json": v_response_json}
        try:
            db.session.execute(query, params)
            db.session.commit()
        except Exception as e:
            print(e, flush=True)
            db.session.rollback()
        finally:
            db.session.close()

    def MakeResponse(api_name, trace_id, status, message, request_json, response_json):
        # 200 - OK
        # 204 - no records found, and that's OK
        Trace.Log(api_name, trace_id, status, message, request_json, str(response_json))

        resp = response_json
        resp.headers['Trace-Id'] = trace_id
        resp.status = status
        return resp

    def MakeError(api_name, trace_id, status, message, request_json, error_code):
        # 400 - bad request/malformed json request
        # 404 - data not found, and that's not OK
        # 500 - internal server error - issue in our code?
        resp = {}
        resp["code"] = error_code
        resp["message"] = message
        resp["serviceName"] = "AI Engine"
        resp["traceId"] = trace_id

        Trace.Log(api_name, trace_id, status, message, request_json, str(resp))

        #resp = resp
        resp.headers['Trace-Id'] = trace_id
        resp.status = status
        return resp

    def AddNewTrace(api_name, status, request_json):
        """
        Adds a new trace and sql function returns record and trace id
        :param status:
        :param request_json:
        :return:
        """
        # create new trace before calling an API
        v_request_json = request_json.replace("\'", '\"').replace('None', 'null').replace('True', 'true').replace(
            'False', 'false')
        query1 = "select * from public.trace_add_new (:p_api_name, :p_status, :p_request_json); "
        params1 = {"p_api_name": api_name, "p_status": status, "p_request_json": v_request_json}

        try:
            rows = db.session.execute(query1, params1).fetchall()
            db.session.commit()
        except Exception as e:
            print(e, flush=True)
            db.session.rollback()
        finally:
            db.session.close()
        return rows[0]["RecordId"], rows[0]["Trace-Id"]
