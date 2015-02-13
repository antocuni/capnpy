from capnpy.convert_case import from_camel_case

def test_from_camel_case():
    c = from_camel_case
    assert c('CamelCase') == 'camel_case'
    assert c('CamelCamelCase') == 'camel_camel_case'
    assert c('Camel2Camel2Case') == 'camel2_camel2_case'
    assert c('getHTTPResponseCode') == 'get_http_response_code'
    assert c('get2HTTPResponseCode') == 'get2_http_response_code'
    assert c('HTTPResponseCode') == 'http_response_code'
    assert c('HTTPResponseCodeXYZ') == 'http_response_code_xyz'
