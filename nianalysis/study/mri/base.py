from nipype.pipeline import engine as pe
from nipype.interfaces import fsl
from nianalysis.dataset import Dataset
from nianalysis.study.base import Study, set_dataset_specs
from nianalysis.requirements import Requirement
from nianalysis.citations import fsl_cite, bet_cite, bet2_cite
from nianalysis.data_formats import nifti_gz_format


class MRStudy(Study):

    def brain_mask_pipeline(self, robust=True, **kwargs):  # @UnusedVariable
        """
        Generates a whole brain mask using MRtrix's 'dwi2mask' command
        """
        pipeline = self._create_pipeline(
            name='brain_mask',
            inputs=['mri_scan'],
            outputs=['masked_mri_scan', 'brain_mask'],
            description="Generate brain mask from mri_scan",
            options={},
            requirements=[Requirement('fsl', min_version=(0, 5, 0))],
            citations=[fsl_cite, bet_cite, bet2_cite], approx_runtime=5)
        # Create mask node
        bet = pe.Node(interface=fsl.BET(), name="bet")
        bet.inputs.mask = True
        bet.inputs.robust = robust
        # Connect inputs/outputs
        pipeline.connect_input('mri_scan', bet, 'in_file')
        pipeline.connect_output('masked_mri_scan', bet, 'out_file')
        pipeline.connect_output('brain_mask', bet, 'mask_file')
        # Check inputs/outputs are connected
        pipeline.assert_connected()
        return pipeline

    def eroded_mask_pipeline(self, **kwargs):
        raise NotImplementedError

    _components = set_dataset_specs(
        Dataset('mri_scan', nifti_gz_format),
        Dataset('masked_mri_scan', nifti_gz_format, brain_mask_pipeline),
        Dataset('brain_mask', nifti_gz_format, brain_mask_pipeline),
        Dataset('eroded_mask', nifti_gz_format, eroded_mask_pipeline))
