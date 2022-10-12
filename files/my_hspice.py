import textwrap

def read_hspice_tr(filename):
    def _get_variables_from_header(header):
        # Variable names are found after 'TIME'
        variables = []
        for item in header.split():
            if (item == 'TIME'):
                variables.clear()
                variables.append('TIME')
            else:
                variables.append(item + ')')
        return variables

    def _get_float_from_dataset(content):
        # Each data item is 13 chars, in exponential format
        my_list = textwrap.wrap(content, 13,
                    drop_whitespace=True,
                    break_on_hyphens=False)
        my_list = list(map(float, my_list))
        return my_list
    
    # Retrieve file contents
    with open(filename) as f:
        content = f.read().replace('\n', '')

    # Split up into list of variables and data
    header = content.split('$&%#')[0]
    dataset = content.split('$&%#')[1].strip()
    list_vars = _get_variables_from_header(header)
    list_data = _get_float_from_dataset(dataset)

    # Package it into a dict
    my_dict = {}
    
    ## Create the key, each holding a list
    for v in list_vars:
        my_dict[v] = list()
    
    ## Fill in the values of the respective list
    for i, item in enumerate(list_data):
        dict_index = i % len(list_vars)
        key = list_vars[dict_index]
        my_dict[key].append(item)

    return my_dict
