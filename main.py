from dash.dependencies import Input, Output, State, ClientsideFunction, ALL
from dash import dcc
from dash import html
import cufflinks
import base64
import dash
import i18n
import os
import sys
import time
import urllib
import zipfile
from app.cache import cache, cache_timeout, make_cache_key_for_configs
from app.process_uploaded_file import process_uploaded_file
from app.config import Config
from app.header import Header
from app.generate_divs import GenerateDivs
import app.constants

i18n.set('filename_format', '{locale}.{format}')
i18n.load_path.append('.')

cufflinks.go_offline()
cufflinks.set_config_file(world_readable=True, theme='white')

external_scripts = [
        {
            'src': 'https://code.jquery.com/jquery-3.5.1.slim.min.js',
            'integrity': 'sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj',
            'crossorigin': 'anonymous'
        },
        {
            'src': 'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
            'integrity': 'sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo',
            'crossorigin': 'anonymous'
        },
        {
            'src': 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js',
            'integrity': 'sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI',
            'crossorigin': 'anonymous'
        }
    ]

external_stylesheets = [
        {
            'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css',
            'rel': 'stylesheet',
            'integrity': 'sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk',
            'crossorigin': 'anonymous'
        }
    ]

dash_app = dash.Dash(__name__,
                     external_scripts=external_scripts,
                     external_stylesheets=external_stylesheets)

server = dash_app.server
cache.init_app(server, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'cache'})

dash_app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div([], id='header'),
    html.Div([
            html.Label(i18n.t('layout.model'), htmlFor='input-string'),
            dcc.Input(id='input-string', type='text', className='input-field mb-3'),
            html.Label(i18n.t('layout.compare_to'), htmlFor='compare-to'),
            dcc.Input(id='compare-to', type='text', className='input-field mb-1'),
            html.Br(),
            html.Button(id='submit-button', n_clicks=0, children=i18n.t('layout.submit')),
            html.Button(
                id='clear-cache',
                n_clicks=0,
                children=i18n.t('layout.clear_cache'),
                className='clear-cache-button',
                ),
        ],
        className='source-form'
    ),
    html.Hr(),
    dcc.Upload(
        id='upload-data',
        children=html.Div(html.Button(i18n.t('layout.upload_zip_file'))),
        className='upload-zone',
    ),
    html.Nav([
        html.A(
                i18n.t('tab.all'),
                className='nav-item nav-link active',
                id='nav-all-tab',
                href='#nav-all',
                role='tab',
                **{'data-toggle': 'tab'},
                ),
        html.A(
                i18n.t('tab.climate'),
                className='nav-item nav-link',
                id='nav-climate-tab',
                href='#nav-climate',
                role='tab',
                **{'data-toggle': 'tab'},
            ),
        html.A(
                i18n.t('tab.land'),
                className='nav-item nav-link',
                id='nav-land-tab',
                href='#nav-land',
                role='tab',
                **{'data-toggle': 'tab'},
                ),
        html.A(
                i18n.t('tab.energy'),
                className='nav-item nav-link',
                id='nav-energy-tab',
                href='#nav-energy',
                role='tab',
                **{'data-toggle': 'tab'},
                ),
        html.A(
                i18n.t('tab.water'),
                className='nav-item nav-link',
                id='nav-water-tab',
                href='#nav-water',
                role='tab',
                **{'data-toggle': 'tab'},
                ),
    ], className='nav nav-tabs justify-content-center', id='categoryTab', role='tablist'),
    dcc.Loading(html.Div([
            html.Div([], className='tab-pane show active', id='nav-all', role='tabpanel'),
            html.Div([], className='tab-pane show', id='nav-climate', role='tabpanel'),
            html.Div([], className='tab-pane show', id='nav-land', role='tabpanel'),
            html.Div([], className='tab-pane show', id='nav-energy', role='tabpanel'),
            html.Div([], className='tab-pane show', id='nav-water', role='tabpanel'),
        ], id='categoryTabContent', className='tab-content'), fullscreen=True),
])


dash_app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='testFunction'
    ),
    Output(component_id='categoryTabContent', component_property='data-checked-boxes'),
    [Input({'type': 'checkboxes', 'index': ALL}, 'value')],
    [State({'type': 'checkboxes', 'index': ALL}, 'options')],
)


@dash_app.callback(
    Output(component_id='clear-cache', component_property='data-clear-cache'),
    [Input(component_id='clear-cache', component_property='n_clicks')]
    )
def clear_cache(n_clicks):
    if n_clicks > 0:
        print('setting deleting cache')
        return True
    else:
        return False


@dash_app.callback(
    [Output(component_id={'type': 'checkboxes', 'index': ALL}, component_property='value')],
    [Input(component_id={'type': 'select-all', 'index': ALL}, component_property='n_clicks')],
    [
        State({'type': 'checkboxes', 'index': ALL}, 'value'),
        State({'type': 'checkboxes', 'index': ALL}, 'options'),
    ]
    )
def toggle_all(n_clicks, current_value, options):
    result = []
    for i, n_click in enumerate(n_clicks, start=0):
        all_values = [option['value'] for option in options[i]]
        if n_click is None:
            result.append(current_value[i])
        elif n_click % 2 == 0:
            result.append(all_values)
        else:
            result.append([])
    return [result]


@dash_app.callback(
    Output(component_id='header', component_property='children'),
    [
        Input(component_id='submit-button', component_property='n_clicks'),
        Input(component_id='input-string', component_property='n_submit'),
        Input(component_id='url', component_property='search'),
        Input(component_id='upload-data', component_property='contents'),
    ],
    [State('input-string', 'value')]
    )
def generate_header(n_clicks, n_submit, raw_query_string, upload_data, input_string):
    triggered_element = dash.callback_context.triggered[0]['prop_id']
    config_input = config_input_from(input_string, raw_query_string, triggered_element)
    config = Config(config_input)
    return Header(config).contents()


@dash_app.callback(
    [
        Output(component_id='nav-all', component_property='children'),
        Output(component_id='nav-climate', component_property='children'),
        Output(component_id='nav-land', component_property='children'),
        Output(component_id='nav-energy', component_property='children'),
        Output(component_id='nav-water', component_property='children'),
    ],
    [
        Input(component_id='submit-button', component_property='n_clicks'),
        Input(component_id='input-string', component_property='n_submit'),
        Input(component_id='url', component_property='search'),
        Input(component_id='upload-data', component_property='contents'),
        Input(component_id='clear-cache', component_property='data-clear-cache'),
    ],
    [
        State('input-string', 'value'),
        State('compare-to', 'value'),
    ]
    )
def generate_figure_divs(
        n_clicks, n_submit, raw_query_string, upload_data, clear_cache,
        input_string, compare_to,
        ):
    triggered_element = dash.callback_context.triggered[0]['prop_id']
    main_config_input = config_input_from(input_string, raw_query_string, triggered_element)
    configs = [
            Config(config_input) for config_input in [main_config_input, compare_to]
    ]
    valid_configs = [config for config in configs if config.is_valid()]

    if clear_cache:
        cache.delete_memoized(generate_divs, valid_configs)

    if len(valid_configs) > 0:
        language = parse_query_string(raw_query_string)["locale"]
        i18n.set('locale', language)
        app.constants.set_cols_from_language(language)
        return generate_divs(valid_configs)
    else:
        return [f'Invalid models: {[config.input_string for config in configs]}', '', '', '', '']


@dash_app.callback(
    Output(component_id='input-string', component_property='value'),
    [Input(component_id='url', component_property='search')]
    )
def populate_input_string_from_query_string(query_string):
    if query_string is not None:
        print(f'populating query_string {query_string}')
        return parse_query_string(query_string)["model"]
    else:
        return ''


@cache.memoize(timeout=cache_timeout())
def generate_divs(configs):
    start = time.time()
    divs = GenerateDivs(configs).generate_divs()
    end = time.time()
    print(f'Generated visualization in {round(end - start, 2)}s')
    return divs


generate_divs.make_cache_key = make_cache_key_for_configs


def config_input_from(input_string, raw_query_string, triggered_element=''):
    config_input = input_string

    if input_string is None and raw_query_string is None:
        return ''

    if input_string is None and raw_query_string is not None:  # First initialization
        config_input = parse_query_string(raw_query_string)["model"]

    if triggered_element in ['upload-data.contents']:
        config_input = process_uploaded_file(upload_data)

    return config_input


def parse_query_string(query_string):
    parsed_qs = urllib.parse.parse_qs(
        urllib.parse.unquote(query_string)
    )
    return {"model": parsed_qs.get('?model', [''])[0], "locale": parsed_qs.get("locale", "en")[0]}


if __name__ == '__main__':
    if 'DASH_DEBUG' in os.environ:
        dash_app.run_server(debug=True)
    else:
        dash_app.run_server(debug=False)
