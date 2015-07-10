from django.shortcuts import render

from tethys_apps.sdk.gizmos import *


def home(request):
    """
    Controller for the app home page.
    """
    peak_flow_slider = RangeSlider(
                display_text='Peak Flow (cms)',
                name='peak_flow',
                min=500,
                max=1200,
                initial=800,
                step=50
    )

    time_peak_slider = RangeSlider(
                display_text='Time to Peak (hrs.)',
                name='time_to_peak',
                min=1,
                max=12,
                initial=6,
                step=1
    )

    peak_duration_slider = RangeSlider(
                display_text='Peak Duration (hrs.)',
                name='peak_duration',
                min=1,
                max=12,
                initial=6,
                step=1
    )

    falling_limb_duration = RangeSlider(
                display_text='Falling Limb Duration (hrs.)',
                name='falling_limb_duration',
                min=12,
                max=48,
                initial=24,
                step=1
    )

    submit_button = Button(
                display_text='Generate Hydrograph',
                name='submit',
                attributes='form=hydrograph-form',
                submit=True
    )

    if request.POST  and 'submit' in request.POST:
        peak_flow = request.POST['peak_flow']
        time_to_peak = request.POST['time_to_peak']
        peak_duration = request.POST['peak_duration']
        falling_limb_duration = request.POST['falling_limb_duration']


    context = {'peak_flow_slider': peak_flow_slider,
               'time_peak_slider': time_peak_slider,
               'peak_duration_slider': peak_duration_slider,
               'falling_limb_duration': falling_limb_duration,
               'submit_button': submit_button
    }

    return render(request, 'dam_break/home.html', context)