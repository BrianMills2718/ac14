"""AC14 generated component for computing Option A zomma."""

import math


class GeneratedComponent:
    """Compute Option A zomma from Option A params and gamma output."""

    _PARAMS_PORT = "option_a_params_output"
    _GAMMA_PORT = "option_a_gamma_output"
    _OUTPUT_PORT = "option_a_zomma_output"
    _PARAMS_FIELDS = (
        "case_id",
        "spot_a",
        "strike_a",
        "rate_a",
        "vol_a",
        "T_a",
        "zeta_a",
        "alpha_a",
        "spot_b",
        "strike_b",
        "rate_b",
        "vol_b",
        "T_b",
        "zeta_b",
        "alpha_b",
        "d1_zeta_a",
        "d2_zeta_a",
        "disc_alpha_a",
        "dd1_dT_a",
    )
    _GAMMA_FIELDS = _PARAMS_FIELDS + ("gamma_a",)

    def execute(self, inputs):
        """Execute the packet contract using plain dict inputs and outputs."""
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a dict keyed by input port name")
        if self._PARAMS_PORT not in inputs:
            raise ValueError("missing required input port: option_a_params_output")
        if self._GAMMA_PORT not in inputs:
            raise ValueError("missing required input port: option_a_gamma_output")

        params = inputs[self._PARAMS_PORT]
        gamma_output = inputs[self._GAMMA_PORT]
        if not isinstance(params, dict):
            raise ValueError("input port option_a_params_output must contain a dict")
        if not isinstance(gamma_output, dict):
            raise ValueError("input port option_a_gamma_output must contain a dict")

        missing_params = [field for field in self._PARAMS_FIELDS if field not in params]
        if missing_params:
            raise ValueError(
                "missing required input fields for option_a_params_output: "
                + ", ".join(missing_params)
            )

        missing_gamma = [
            field for field in self._GAMMA_FIELDS if field not in gamma_output
        ]
        if missing_gamma:
            raise ValueError(
                "missing required input fields for option_a_gamma_output: "
                + ", ".join(missing_gamma)
            )

        case_id = params["case_id"]
        if not isinstance(case_id, str):
            raise ValueError("case_id must be a string")
        if gamma_output["case_id"] != case_id:
            raise ValueError(
                "case_id mismatch between option_a_params_output and option_a_gamma_output"
            )

        for field in self._PARAMS_FIELDS[1:]:
            left_value = self._as_number(params[field], field)
            right_value = self._as_number(gamma_output[field], field)
            if left_value != right_value:
                raise ValueError(
                    "field mismatch between option_a_params_output and option_a_gamma_output: "
                    + field
                )

        vol_a = self._as_number(params["vol_a"], "vol_a")
        d1_zeta_a = self._as_number(params["d1_zeta_a"], "d1_zeta_a")
        d2_zeta_a = self._as_number(params["d2_zeta_a"], "d2_zeta_a")
        gamma_a = self._as_number(gamma_output["gamma_a"], "gamma_a")

        if vol_a <= 0.0:
            raise ValueError("vol_a must be > 0")

        zomma_a = gamma_a * ((d1_zeta_a * d2_zeta_a) - 1.0) / vol_a
        if not math.isfinite(zomma_a):
            raise ValueError("computed zomma_a is not finite")

        output = dict(params)
        output["zomma_a"] = zomma_a
        return {self._OUTPUT_PORT: output}

    @staticmethod
    def _as_number(value, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a real number")
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            raise ValueError(f"{field_name} must be finite")
        return numeric_value


def build_component():
    """Build the generated AC14 component."""
    return GeneratedComponent()
