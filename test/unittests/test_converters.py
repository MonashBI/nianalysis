from arcana.data import InputFilesetSpec, FilesetSpec, FilesetFilter
from banana.file_format import (
    dicom_format, nifti_format, text_format, directory_format,
    zip_format)
from arcana.analysis.base import Analysis, AnalysisMetaClass
from arcana.utils.testing import BaseTestCase
from nipype.interfaces.utility import IdentityInterface


class ConversionAnalysis(Analysis, metaclass=AnalysisMetaClass):

    add_data_specs = [
        InputFilesetSpec('mrtrix', text_format),
        InputFilesetSpec('nifti_gz', text_format),
        InputFilesetSpec('dicom', dicom_format),
        InputFilesetSpec('directory', directory_format),
        InputFilesetSpec('zip', zip_format),
        FilesetSpec('nifti_gz_from_dicom', text_format, 'conv_pipeline'),
        FilesetSpec('mrtrix_from_nifti_gz', text_format, 'conv_pipeline'),
        FilesetSpec('nifti_from_mrtrix', nifti_format, 'conv_pipeline'),
        FilesetSpec('directory_from_zip', directory_format, 'conv_pipeline'),
        FilesetSpec('zip_from_directory', zip_format, 'conv_pipeline')]

    def conv_pipeline(self):
        pipeline = self.new_pipeline(
            name='conv_pipeline',
            desc=("A pipeline that tests out various data format conversions"),
            citations=[],)
        # Convert from DICOM to NIfTI.gz format on input
        nifti_gz_from_dicom = pipeline.add(
            'nifti_gz_from_dicom',
            IdentityInterface(
                fields=['file']))
        pipeline.connect_input('dicom', nifti_gz_from_dicom,
                               'file')
        pipeline.connect_output('nifti_gz_from_dicom', nifti_gz_from_dicom,
                                'file')
        # Convert from NIfTI.gz to MRtrix format on output
        mrtrix_from_nifti_gz = pipeline.add(
            'mrtrix_from_nifti_gz',
            IdentityInterface(fields=['file']))
        pipeline.connect_input('nifti_gz', mrtrix_from_nifti_gz,
                               'file')
        pipeline.connect_output('mrtrix_from_nifti_gz', mrtrix_from_nifti_gz,
                                'file')
        # Convert from MRtrix to NIfTI format on output
        nifti_from_mrtrix = pipeline.add(
            'nifti_from_mrtrix',
            IdentityInterface(fields=['file']))
        pipeline.connect_input('mrtrix', nifti_from_mrtrix,
                               'file')
        pipeline.connect_output('nifti_from_mrtrix', nifti_from_mrtrix,
                                'file')
        # Convert from zip file to directory format on input
        directory_from_zip = pipeline.add(
            'directory_from_zip',
            IdentityInterface(fields=['file']),)
        pipeline.connect_input('zip', directory_from_zip,
                               'file')
        pipeline.connect_output('directory_from_zip', directory_from_zip,
                                'file')
        # Convert from NIfTI.gz to MRtrix format on output
        zip_from_directory = pipeline.add(
            'zip_from_directory',
            IdentityInterface(fields=['file']))
        pipeline.connect_input('directory', zip_from_directory,
                               'file')
        pipeline.connect_output('zip_from_directory', zip_from_directory,
                                'file')
        return pipeline


class TestFormatConversions(BaseTestCase):

    def test_pipeline_prerequisites(self):
        analysis = self.create_analysis(
            ConversionAnalysis, 'conversion', [
                FilesetFilter('mrtrix', 'mrtrix', text_format),
                FilesetFilter('nifti_gz', text_format,
                              'nifti_gz'),
                FilesetFilter('dicom', dicom_format,
                              't1_mprage_sag_p2_iso_1_ADNI'),
                FilesetFilter('directory', directory_format,
                              't1_mprage_sag_p2_iso_1_ADNI'),
                FilesetFilter('zip', 'zip', zip_format)])
        self.assertFilesetCreated(
            next(iter(analysis.data('nifti_gz_from_dicom', derive=True))))
        self.assertFilesetCreated(
            next(iter(analysis.data('mrtrix_from_nifti_gz', derive=True))))
        self.assertFilesetCreated(
            next(iter(analysis.data('nifti_from_mrtrix', derive=True))))
        self.assertFilesetCreated(
            next(iter(analysis.data('directory_from_zip', derive=True))))
        self.assertFilesetCreated(
            next(iter(analysis.data('zip_from_directory', derive=True))))
