"""Imports"""
import json
import pytest
import demistomock as demisto
from socket import inet_aton

IOC_RES_LEN = 38

'''Tests'''


@pytest.mark.helper_commands
class TestHelperFunctions:
    @pytest.mark.list_to_str
    def test_list_to_str_1(self):
        """Test invalid"""
        from EDL import list_to_str
        with pytest.raises(AttributeError):
            invalid_list_value = 2
            list_to_str(invalid_list_value)

        with pytest.raises(AttributeError):
            invalid_list_value = {'invalid': 'invalid'}
            list_to_str(invalid_list_value)

    @pytest.mark.list_to_str
    def test_list_to_str_2(self):
        """Test empty"""
        from EDL import list_to_str
        assert list_to_str(None) == ''
        assert list_to_str([]) == ''
        assert list_to_str({}) == ''

    @pytest.mark.list_to_str
    def test_list_to_str_3(self):
        """Test non empty fields"""
        from EDL import list_to_str
        valid_list_value = [1, 2, 3, 4]
        assert list_to_str(valid_list_value) == '1,2,3,4'
        assert list_to_str(valid_list_value, '.') == '1.2.3.4'
        assert list_to_str(valid_list_value, map_func=lambda x: f'{x}a') == '1a,2a,3a,4a'

    @pytest.mark.get_params_port
    def test_get_params_port_1(self):
        """Test invalid"""
        from EDL import get_params_port
        params = {'longRunningPort': 'invalid'}
        with pytest.raises(ValueError):
            get_params_port(params)

    @pytest.mark.get_params_port
    def test_get_params_port_2(self):
        """Test empty"""
        from EDL import get_params_port
        params = {'longRunningPort': ''}
        with pytest.raises(ValueError):
            get_params_port(params)

    @pytest.mark.get_params_port
    def test_get_params_port_3(self):
        """Test valid"""
        from EDL import get_params_port
        params = {'longRunningPort': '80'}
        assert get_params_port(params) == 80

    @pytest.mark.refresh_value_cache
    def test_refresh_value_cache_1(self, mocker):
        """Test out_format=text"""
        import EDL as edl
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            mocker.patch.object(edl, 'find_indicators_to_limit', return_value=json.loads(iocs_json_f.read()))
            edl_vals = edl.refresh_value_cache(indicator_query='', out_format='text')
            assert len(edl_vals) == IOC_RES_LEN
            for ip in edl_vals:
                assert inet_aton(ip)  # assert all lines are ips

    @pytest.mark.refresh_value_cache
    def test_refresh_value_cache_2(self, mocker):
        """Test out_format=json"""
        import EDL as edl
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            mocker.patch.object(edl, 'find_indicators_to_limit', return_value=iocs_json)
            edl_vals = edl.refresh_value_cache(indicator_query='', out_format='json')
            assert isinstance(edl_vals[0], str)
            edl_vals = json.loads(edl_vals[0])
            assert iocs_json == edl_vals

    @pytest.mark.refresh_value_cache
    def test_refresh_value_cache_3(self, mocker):
        """Test out_format=csv"""
        import EDL as edl
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            mocker.patch.object(edl, 'find_indicators_to_limit', return_value=iocs_json)
            edl_vals = edl.refresh_value_cache(indicator_query='', out_format='csv')
            with open('EDL_test/TestHelperFunctions/iocs_out_csv.json', 'r') as iocs_out_f:
                iocs_out = json.load(iocs_out_f)
                assert iocs_out == edl_vals
                assert len(edl_vals[0].split(',')) == 29  # assert first line is columns line

    @pytest.mark.refresh_value_cache
    def test_refresh_value_cache_4(self, mocker):
        """Test out_format=json-seq"""
        import EDL as edl
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            mocker.patch.object(edl, 'find_indicators_to_limit', return_value=iocs_json)
            edl_vals = edl.refresh_value_cache(indicator_query='', out_format='json-seq')
            with open('EDL_test/TestHelperFunctions/iocs_out_json_seq.json', 'r') as iocs_out_f:
                iocs_out = json.load(iocs_out_f)
                assert iocs_out == edl_vals
                assert len(edl_vals) == IOC_RES_LEN

    @pytest.mark.find_indicators_to_limit
    def test_find_indicators_to_limit_1(self, mocker):
        """Test find indicators limit"""
        import EDL as edl
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            limit = 30
            mocker.patch.object(edl, 'find_indicators_to_limit_loop', return_value=(iocs_json, 1))
            edl_vals = edl.find_indicators_to_limit(indicator_query='', limit=limit)
            assert len(edl_vals) == limit

    @pytest.mark.find_indicators_to_limit_loop
    def test_find_indicators_to_limit_loop_1(self, mocker):
        """Test find indicators stops when reached last page"""
        import EDL as edl
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_dict = {'iocs': json.loads(iocs_json_f.read())}
            limit = 50
            mocker.patch.object(demisto, 'findIndicators', return_value=iocs_dict)
            edl_vals, nxt_pg = edl.find_indicators_to_limit_loop(indicator_query='', limit=limit)
            assert nxt_pg == 1  # assert entered into loop

    @pytest.mark.find_indicators_to_limit_loop
    def test_find_indicators_to_limit_loop_2(self, mocker):
        """Test find indicators stops when reached limit"""
        import EDL as edl
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_dict = {'iocs': json.loads(iocs_json_f.read())}
            limit = 30
            mocker.patch.object(demisto, 'findIndicators', return_value=iocs_dict)
            edl.PAGE_SIZE = IOC_RES_LEN
            edl_vals, nxt_pg = edl.find_indicators_to_limit_loop(indicator_query='', limit=limit,
                                                                 last_found_len=IOC_RES_LEN)
            assert nxt_pg == 1  # assert entered into loop

    @pytest.mark.create_values_out_dict
    def test_create_values_out_dict_1(self):
        """Test CSV out"""
        from EDL import create_values_out_dict, FORMAT_CSV
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            csv_out = create_values_out_dict(iocs_json, FORMAT_CSV)
            assert len(csv_out) == IOC_RES_LEN + 1
            with open('EDL_test/TestHelperFunctions/iocs_out_csv.json', 'r') as iocs_out_f:
                expected_csv_out = json.load(iocs_out_f)
                for csv_line in csv_out.values():
                    assert csv_line in expected_csv_out

    @pytest.mark.create_values_out_dict
    def test_create_values_out_dict_2(self):
        """Test JSON out"""
        from EDL import create_values_out_dict, FORMAT_JSON
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            json_out = json.loads(create_values_out_dict(iocs_json, FORMAT_JSON).get('iocs_list'))
            assert json_out == iocs_json

    @pytest.mark.create_values_out_dict
    def test_create_values_out_dict_3(self):
        """Test JSON_SEQ out"""
        from EDL import create_values_out_dict, FORMAT_JSON_SEQ
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            json_seq_out = create_values_out_dict(iocs_json, FORMAT_JSON_SEQ)
            for seq_line in json_seq_out.values():
                assert json.loads(seq_line) in iocs_json

    @pytest.mark.create_values_out_dict
    def test_create_values_out_dict_4(self):
        """Test TEXT out"""
        from EDL import create_values_out_dict, FORMAT_TEXT
        with open('EDL_test/TestHelperFunctions/demisto_iocs.json', 'r') as iocs_json_f:
            iocs_json = json.loads(iocs_json_f.read())
            text_out = create_values_out_dict(iocs_json, FORMAT_TEXT)
            for key, text_line in text_out.items():
                assert key == text_line

    @pytest.mark.get_edl_ioc_list
    def test_get_edl_ioc_list_1(self, mocker):
        """Test on_demand"""
        from EDL import get_edl_ioc_list
        with open('EDL_test/TestHelperFunctions/iocs_cache_values_text.json', 'r') as iocs_text_values_f:
            iocs_text_dict = json.loads(iocs_text_values_f.read())
            params = {'format': 'text', 'on_demand': True, 'edl_size': 50}
            mocker.patch.object(demisto, 'params', return_value=params)
            mocker.patch.object(demisto, 'getIntegrationContext', return_value=iocs_text_dict)
            ioc_list = get_edl_ioc_list()
            for ioc_row in ioc_list:
                assert ioc_row in iocs_text_dict
