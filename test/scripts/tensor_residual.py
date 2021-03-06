import os.path as op
from arcana import Dataset, SingleProc, StaticEnv, FilesetFilter
from banana.analysis.mri import DwiAnalysis
from banana.file_format import mrtrix_image_format

shell = 'multi'

if shell == 'single':
    dataset_path = '/Users/tclose/Data/single-shell'
else:
    dataset_path = '/Users/tclose/Data/multi-shell'

analysis = DwiAnalysis(
    name='residual_{}'.format(shell),
    dataset=Dataset(dataset_path, depth=0),
    processor=SingleProc(work_dir=op.expanduser('~/work'),
                         reprocess=True),
    environment=StaticEnv(),
    inputs=[FilesetFilter('series', 'dwi', mrtrix_image_format)],
    enforce_inputs=False,
    parameters={'pe_dir': 'RL'})

# print(analysis.b_shells())

# Generate whole brain tracks and return path to cached dataset
residual = analysis.data('tensor_residual', derive=True)

for f in residual:
    print(f"Residual created at {f.path}")
