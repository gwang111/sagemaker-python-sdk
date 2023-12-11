# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from __future__ import absolute_import

from unittest import TestCase
from unittest.mock import Mock, PropertyMock, patch, mock_open

from sagemaker.serve.model_server.djl_serving.prepare import prepare_djl_js_resources

MOCK_MODEL_PATH = "/path/to/mock/model/dir"
MOCK_CODE_DIR = "/path/to/mock/model/dir/code"
MOCK_JUMPSTART_ID = "mock_llm_js_id"
MOCK_TMP_DIR = "tmp123456"
MOCK_COMPRESSED_MODEL_DATA_STR = "s3://jumpstart-cache-prod-us-west-2/huggingface-infer"
"/prepack/v1.0.1/infer-prepack-huggingface-llm-falcon-7b-bf16.tar.gz"
MOCK_UNCOMPRESSED_MODEL_DATA_STR = "s3://jumpstart-cache-prod-us-west-2/huggingface-llm"
"/huggingface-llm-falcon-7b-bf16/artifacts/inference-prepack/v1.0.1/"
MOCK_UNCOMPRESSED_MODEL_DATA_STR_FOR_DICT = "s3://jumpstart-cache-prod-us-west-2/huggingface-llm"
"/huggingface-llm-falcon-7b-bf16/artifacts/inference-prepack/v1.0.1/dict/"
MOCK_UNCOMPRESSED_MODEL_DATA_DICT = {
    "S3DataSource": {
        "S3Uri": MOCK_UNCOMPRESSED_MODEL_DATA_STR_FOR_DICT,
        "S3DataType": "S3Prefix",
        "CompressionType": "None",
    }
}


class DjlPrepareTests(TestCase):
    @patch("sagemaker.serve.model_server.djl_serving.prepare._check_disk_space")
    @patch("sagemaker.serve.model_server.djl_serving.prepare._check_docker_disk_usage")
    @patch("sagemaker.serve.model_server.djl_serving.prepare.Path")
    @patch("sagemaker.serve.model_server.djl_serving.prepare.S3Downloader")
    @patch("sagemaker.serve.model_server.djl_serving.prepare._tmpdir")
    @patch(
        "sagemaker.serve.model_server.djl_serving.prepare._read_existing_serving_properties",
        return_value={},
    )
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("json.load")
    def test_prepare_djl_js_resources_for_jumpstart_uncompressed_str(
        self,
        mock_load,
        mock_open,
        mock_existing_props,
        mock_tmpdir,
        mock_s3downloader,
        mock_path,
        mock_disk_usage,
        mock_disk_space,
    ):
        # mock actions
        (
            mock_model_path,
            mock_code_dir,
            mocked_s3_downloader_obj,
        ) = self.populate_standard_resource_mocks(
            mock_path, mock_s3downloader, mock_tmpdir, mock_load
        )

        # invoke prepare
        existing_properties, hf_model_config, success = prepare_djl_js_resources(
            model_path=MOCK_MODEL_PATH,
            js_id=MOCK_JUMPSTART_ID,
            model_data=MOCK_UNCOMPRESSED_MODEL_DATA_STR,
        )

        # validate call chain
        self.validate_standard_resource_mocks(
            mock_model_path, mock_code_dir, mock_disk_space, mock_disk_usage
        )
        mocked_s3_downloader_obj.download.assert_called_once_with(
            MOCK_UNCOMPRESSED_MODEL_DATA_STR, MOCK_TMP_DIR
        )
        assert existing_properties == {}
        assert hf_model_config == {}
        assert success

    @patch("sagemaker.serve.model_server.djl_serving.prepare._check_disk_space")
    @patch("sagemaker.serve.model_server.djl_serving.prepare._check_docker_disk_usage")
    @patch("sagemaker.serve.model_server.djl_serving.prepare.Path")
    @patch("sagemaker.serve.model_server.djl_serving.prepare.S3Downloader")
    @patch("sagemaker.serve.model_server.djl_serving.prepare._tmpdir")
    @patch(
        "sagemaker.serve.model_server.djl_serving.prepare._read_existing_serving_properties",
        return_value={},
    )
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("json.load")
    def test_prepare_djl_js_resources_for_jumpstart_uncompresssed_dict(
        self,
        mock_load,
        mock_open,
        mock_existing_props,
        mock_tmpdir,
        mock_s3downloader,
        mock_path,
        mock_disk_usage,
        mock_disk_space,
    ):
        # mock actions
        (
            mock_model_path,
            mock_code_dir,
            mocked_s3_downloader_obj,
        ) = self.populate_standard_resource_mocks(
            mock_path, mock_s3downloader, mock_tmpdir, mock_load
        )

        # invoke prepare
        existing_properties, hf_model_config, success = prepare_djl_js_resources(
            model_path=MOCK_MODEL_PATH,
            js_id=MOCK_JUMPSTART_ID,
            model_data=MOCK_UNCOMPRESSED_MODEL_DATA_DICT,
        )

        # validate call chain
        self.validate_standard_resource_mocks(
            mock_model_path, mock_code_dir, mock_disk_space, mock_disk_usage
        )
        mocked_s3_downloader_obj.download.assert_called_once_with(
            MOCK_UNCOMPRESSED_MODEL_DATA_STR_FOR_DICT, MOCK_TMP_DIR
        )
        assert existing_properties == {}
        assert hf_model_config == {}
        assert success

    @patch("sagemaker.serve.model_server.djl_serving.prepare._check_disk_space")
    @patch("sagemaker.serve.model_server.djl_serving.prepare._check_docker_disk_usage")
    @patch("sagemaker.serve.model_server.djl_serving.prepare.Path")
    @patch("sagemaker.serve.model_server.djl_serving.prepare.tarfile")
    @patch("sagemaker.serve.model_server.djl_serving.prepare.S3Downloader")
    @patch("sagemaker.serve.model_server.djl_serving.prepare._tmpdir")
    @patch(
        "sagemaker.serve.model_server.djl_serving.prepare._read_existing_serving_properties",
        return_value={},
    )
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("json.load")
    def test_prepare_djl_js_resources_for_jumpstart_compressed_str(
        self,
        mock_load,
        mock_open,
        mock_existing_props,
        mock_tmpdir,
        mock_s3downloader,
        mock_tarfile,
        mock_path,
        mock_disk_usage,
        mock_disk_space,
    ):
        # mock actions
        (
            mock_model_path,
            mock_code_dir,
            mocked_s3_downloader_obj,
        ) = self.populate_standard_resource_mocks(
            mock_path, mock_s3downloader, mock_tmpdir, mock_load
        )

        mock_resources = Mock()
        mock_tarfile.open.return_value = mock_resources

        # invoke prepare
        existing_properties, hf_model_config, success = prepare_djl_js_resources(
            model_path=MOCK_MODEL_PATH,
            js_id=MOCK_JUMPSTART_ID,
            model_data=MOCK_COMPRESSED_MODEL_DATA_STR,
        )

        # validate call chain
        self.validate_standard_resource_mocks(
            mock_model_path, mock_code_dir, mock_disk_space, mock_disk_usage
        )
        mocked_s3_downloader_obj.download.assert_called_once_with(
            MOCK_COMPRESSED_MODEL_DATA_STR, MOCK_TMP_DIR
        )
        assert existing_properties == {}
        assert hf_model_config == {}
        assert success

    def populate_standard_resource_mocks(
        self, mock_path, mock_s3downloader, mock_tmpdir, mock_load
    ):
        mock_model_path = Mock()
        mock_model_path.exists.return_value = False
        mock_code_dir = Mock()
        mock_config_json = Mock()
        mock_code_dir.joinpath.return_value = mock_config_json
        mock_code_dir.is_file.return_value = True
        mock_model_path.joinpath.return_value = mock_code_dir

        mock_tmp_js_dir = Mock()
        mock_tmp_sourcedir = Mock()
        mock_tmp_js_dir.joinpath.return_value = mock_tmp_sourcedir
        mock_path.side_effect = [mock_model_path, mock_tmp_js_dir]

        mocked_s3_downloader_obj = Mock()
        mock_s3downloader.return_value = mocked_s3_downloader_obj

        mock_tmpdir_obj = Mock()
        mock_js_dir = Mock()
        mock_js_dir.return_value = MOCK_TMP_DIR
        mock_enter = PropertyMock(return_value=mock_js_dir)
        type(mock_tmpdir_obj).__enter__ = mock_enter
        type(mock_tmpdir_obj).__exit__ = PropertyMock(return_value=Mock())
        mock_tmpdir.return_value = mock_tmpdir_obj

        mock_load.return_value = {}

        return mock_model_path, mock_code_dir, mocked_s3_downloader_obj

    def validate_standard_resource_mocks(
        self, mock_model_path, mock_code_dir, mock_disk_space, mock_disk_usage
    ):
        mock_model_path.mkdir.assert_called_once_with(parents=True)
        mock_model_path.joinpath.assert_called_once_with("code")
        mock_code_dir.mkdir.assert_called_once_with(exist_ok=True, parents=True)
        mock_disk_space.assert_called_once_with(mock_model_path)
        mock_disk_usage.assert_called_once()
