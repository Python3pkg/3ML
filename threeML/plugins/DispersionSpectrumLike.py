import copy

from threeML.plugins.SpectrumLike import SpectrumLike
from threeML.plugins.spectrum.binned_spectrum import BinnedSpectrumWithDispersion
from threeML.plugins.OGIP.response import InstrumentResponse

__instrument_name = "General binned spectral data with energy dispersion"

class DispersionSpectrumLike(SpectrumLike):

    def __init__(self, name, observed_spectrum, background_spectrum, verbose=True):


        assert isinstance(observed_spectrum,BinnedSpectrumWithDispersion), "observed spectrum is not an instance of BinnedSpectrumWithDispersion"

        assert observed_spectrum.response is not None, "the observed spectrum does not have a response"

        # assign the response to the plugins

        self._rsp = observed_spectrum.response #type: InstrumentResponse



        super(DispersionSpectrumLike, self).__init__(name=name,
                                                     observed_spectrum=observed_spectrum,
                                                     background_spectrum=background_spectrum,
                                                     verbose=verbose)

    def set_model(self, likelihoodModel):
        """
        Set the model to be used in the joint minimization.
        """

        # Store likelihood model

        self._like_model = likelihoodModel

        # We assume there are no extended sources, since we cannot handle them here

        assert self._like_model.get_number_of_extended_sources() == 0, "OGIP-like plugins do not support " \
                                                                       "extended sources"

        # Get the differential flux function, and the integral function, with no dispersion,
        # we simply integrate the model over the bins

        differential_flux, integral = self._get_diff_flux_and_integral()

        self._rsp.set_function(integral)

    def _evaluate_model(self):
        """
        evaluates the full model over all channels
        :return:
        """

        return self._rsp.convolve()

    def get_simulated_dataset(self, new_name=None,**kwargs):
        """
        Returns another DispersionSpectrumLike instance where data have been obtained by randomizing the current expectation from the
        model, as well as from the background (depending on the respective noise models)

        :return: a DispersionSpectrumLike simulated instance
         """

        # pass the response thru to the constructor
        return super(DispersionSpectrumLike, self).get_simulated_dataset(new_name=new_name,
                                                                         response=self._rsp,
                                                                         **kwargs)

    def get_pha_files(self):
        info = {}

        # we want to pass copies so that
        # the user doesn't grab the instance
        # and try to modify things. protection
        info['pha'] = copy.copy(self._observed_spectrum)
        info['bak'] = copy.copy(self._background_spectrum)
        info['rsp'] = copy.copy(self._rsp)

        return info

    def display_rsp(self):
        """
        Display the currently loaded full response matrix, i.e., RMF and ARF convolved
        :return:
        """

        self._rsp.plot_matrix()

