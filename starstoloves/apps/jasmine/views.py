from django.shortcuts import render
from django.contrib.staticfiles import finders

import json

def find_specs():
    finders_list = finders.get_finders()
    filepaths = [];
    for finder in finders_list:
        filepaths += [file_tuple[0] for file_tuple in finder.list([])]
    specs = [
        path[3:-3] for path in filepaths
        if path.startswith('js/') and path.endswith('.spec.js')
    ]
    return specs

def spec_runner(request):
    context = {
        'specs': json.dumps(find_specs())
    }
    return render(request, 'SpecRunner.html', context)