__author__ = 'saeedamen'

#
# Copyright 2020 Cuemacro
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and limitations under the License.
#

"""
Shows how to use finmarketpy to process FX vol surfaces which have been interpolated (uses FinancePy underneath).

Note, you will need to have a Bloomberg terminal (with blpapi Python library) to download the FX market data in order
to plot these vol surface (FX spot, FX forwards, FX implied volatility quotes and deposits)
"""

# For plotting
from chartpy import Chart, Style

# For loading market data
from findatapy.market import Market, MarketDataGenerator, MarketDataRequest

from findatapy.util.loggermanager import LoggerManager

from finmarketpy.volatility.fxvolsurface import FXVolSurface

logger = LoggerManager().getLogger(__name__)

chart = Chart(engine='plotly')
market = Market(market_data_generator=MarketDataGenerator())

# Choose run_example = 0 for everything
# run_example = 1 - plot GBPUSD 1W implied vol
# run_example = 2 - get GBPUSD vol surface for a specific point
# run_example = 3 - do an animation of GBPUSD vol surface over this period
# run_example = 4 - get implied vol for a particular strike, interpolating the surface

run_example = 3

###### Fetch market data for pricing GBPUSD FX options over Brexit vote (ie. FX spot, FX forwards, FX deposits and FX vol quotes)
###### Show how to plot ATM 1M implied vol time series
if run_example == 1 or run_example == 0:
    # Download the whole all market data for GBPUSD for pricing options (vol surface)
    md_request = MarketDataRequest(start_date='01 May 2016', finish_date='01 Aug 2016',
                                   data_source='bloomberg', cut='LDN', category='fx-vol-market',
                                   tickers=['GBPUSD'],
                                   cache_algo='cache_algo_return')

    df = market.fetch_market(md_request)

    style = Style()

    style.title = 'GBPUSD 1M Implied Vol'
    style.scale_factor = 3
    style.source = 'Bloomberg'

    chart.plot(df['GBPUSDV1M.close'], style=style)

###### Fetch market data for pricing GBPUSD FX options over Brexit vote (ie. FX spot, FX forwards, FX deposits and FX vol quotes)
###### Construct volatility surface using FinancePy library underneath, using polynomial interpolation
if run_example == 2 or run_example == 0:
    # Download the whole all market data for GBPUSD for pricing options (vol surface)
    md_request = MarketDataRequest(start_date='20 Jun 2016', finish_date='20 Jun 2016',
                                   data_source='bloomberg', cut='LDN', category='fx-vol-market',
                                   tickers=['GBPUSD'],
                                   cache_algo='cache_algo_return')

    df = market.fetch_market(md_request)

    fx_vol_surface = FXVolSurface(market_df=df)

    fx_vol_surface.build_vol_surface('20 Jun 2016', 'GBPUSD')

    # Note for unstable vol surface dates (eg. over Brexit date) you may need to increase tolerance in FinancePy
    # FinFXVolSurface.buildVolSurface method to get it to fill
    df_vol_dict = fx_vol_surface.extract_vol_surface()

    # Print out the various vol surface and data produced
    print(df_vol_dict['vol_surface_strike_space'])
    print(df_vol_dict['vol_surface_delta_space'])
    print(df_vol_dict['deltas_vs_strikes'])
    print(df_vol_dict['vol_surface_quoted_points'])

    # Plot vol surface animation in strike space (all interpolated)
    # x_axis = strike - index
    # y_axis = tenor - columns
    # z_axis = implied vol - values
    style = Style(title='Plotting in strike space')

    chart.plot(df_vol_dict['vol_surface_strike_space'].iloc[:, ::-1], chart_type='surface', style=style)

    # Plot vol surface in delta space
    chart.plot(df_vol_dict['vol_surface_delta_space'].iloc[:, ::-1],
               chart_type='surface', style=Style(title='Plotting in delta space'))

###### Fetch market data for pricing GBPUSD FX options over Brexit vote (ie. FX spot, FX forwards, FX deposits and FX vol quotes)
###### Do animation for vol surface
if run_example == 3 or run_example == 0:
    # Download the whole all market data for GBPUSD for pricing options (vol surface)
    # Using LDN close data (CMPL)
    md_request = MarketDataRequest(start_date='01 Jun 2016', finish_date='30 Jun 2016',
                                   data_source='bloomberg', cut='LDN', category='fx-vol-market',
                                   tickers=['GBPUSD'],
                                   cache_algo='cache_algo_return')
    # 01 Jun 2016, 30 Jun 2016
    # 20 Jun 2016, 25 Jun 2016

    df = market.fetch_market(md_request)

    fx_vol_surface = FXVolSurface(market_df=df)

    animate_titles = []

    # Note for unstable vol surface dates (eg. over Brexit date) you may need to increase tolerance in FinancePy
    # FinFXVolSurface.buildVolSurface method to get it to fill - or just change dates and currency pair

    # Note this does take a few minutes, given it's fitting the vol surface for every date
    # TODO explore speeding up using Numba or similar
    vol_surface_dict, extremes_dict = fx_vol_surface.extract_vol_surface_across_dates(df.index, 'GBPUSD',
                                         vol_surface_type='vol_surface_strike_space')

    animate_titles = [x.strftime('%d %b %Y') for x in vol_surface_dict.keys()]

    print(extremes_dict)

    # Plot vol surface animation in strike space (all interpolated)
    # x_axis = strike - index
    # y_axis = tenor - columns
    # z_axis = implied vol - values
    style = Style(title='Plotting in strike space', animate_figure=True, animate_titles=animate_titles)

    chart.plot(list(vol_surface_dict.values()), chart_type='surface', style=style)

###### Fetch market data for pricing GBPUSD FX options over Brexit vote (ie. FX spot, FX forwards, FX deposits and FX vol quotes)
###### Get implied vol for specific strikes interpolating across surface
if run_example == 4 or run_example == 0:
    # Download the whole all market data for GBPUSD for pricing options (vol surface)
    md_request = MarketDataRequest(start_date='20 Jun 2016', finish_date='25 Jun 2016',
                                   data_source='bloomberg', cut='LDN', category='fx-vol-market',
                                   tickers=['GBPUSD'],
                                   cache_algo='cache_algo_return')

    df = market.fetch_market(md_request)

    fx_vol_surface = FXVolSurface(market_df=df)

    df_vol_surface_strike_space_list = []
    animate_titles = []

    fx_vol_surface.build_vol_surface('20 Jun 2016', 'GBPUSD')

    # Get the implied volatility for a specific strike (GBPUSD=1.4000 in the 1W tenor) for 20 Jun 2016
    vol_at_strike = fx_vol_surface.calculate_vol_for_strike_expiry(1.4000, tenor='1W')

    fx_vol_surface.build_vol_surface('23 Jun 2016', 'GBPUSD')

    # Get the implied volatility for a specific strike (GBPUSD=1.4000 in the 1W tenor) for 23 Jun 2016
    vol_at_strike = fx_vol_surface.calculate_vol_for_strike_expiry(1.4000, tenor='1W')
