from copy import copy
from arcana.analysis import (
    Analysis as ArcanaAnalysis, MultiAnalysis as ArcanaMultiAnalysis,
     AnalysisMetaClass, MultiAnalysisMetaClass)  # noqa: E501 @UnusedImport
from banana.bids_ import BidsAssocInputs


# Extend Arcana Analysis class to support implicit BIDS selectors

# TODO: need to extend for MultiAnalysis's too

class BidsMixin():

    def __init__(self, name, dataset, processor, inputs=None,
                 bids_task=None, **kwargs):
        if inputs is None:
            inputs = {}
        elif not isinstance(inputs, dict):
            inputs = {i.spec_name: i for i in inputs}
        # IDs need to be set here before the analysis tree is accessed
        self._bids_task = bids_task
        # Attempt to preload default bids inputs
        if dataset.type == 'bids':
            # If the analysis has the attribute default bids inputs then
            # then check to see if they are present in the repository
            bids_inputs = self.get_bids_inputs(bids_task)
            # Combine explicit inputs with defaults, overriding any with
            # matching spec names
            bids_inputs.update(inputs)
            inputs = bids_inputs
        # Update the inputs di
        super().__init__(name, dataset, processor, inputs, **kwargs)

    @classmethod
    def get_bids_inputs(cls, task=None, repository=None):
        if issubclass(cls, MultiAnalysis):
            default_bids_inputs = {}
            for spec in cls.subcomp_specs():
                if hasattr(spec.analysis_class, 'default_bids_inputs'):
                    for inpt in spec.analysis_class.default_bids_inputs:
                        if isinstance(inpt, BidsAssocInputs):
                            inpt = copy(inpt)
                            inpt.prefixed_primary_name = spec.apply_prefix(
                                inpt.primary.name)
                        default_bids_inputs[
                            spec.apply_prefix(inpt.name)] = inpt
        else:
            try:
                default_bids_inputs = {
                    i.name: i for i in cls.default_bids_inputs}
            except AttributeError:
                default_bids_inputs = {}
        inputs = {}
        for name, inpt in default_bids_inputs.items():
            inpt = copy(inpt)
            if inpt.task is None and task is not None:
                inpt.task = task
            inpt._repository = repository
            inputs[name] = inpt
        return inputs

    @property
    def bids_task(self):
        return self._bids_task


class Analysis(BidsMixin, ArcanaAnalysis):
    pass


class MultiAnalysis(BidsMixin, ArcanaMultiAnalysis):
    pass

