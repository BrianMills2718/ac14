"""AC14 generated component for computing the Option B put price."""

import math


class GeneratedComponent:
    """Compute the zeta-modified Option B put price and return the expanded packet."""

    _INPUT_PORT = "option_b_params_output"
    _OUTPUT_PORT = "option_b_put_output"
    _REQUIRED_FIELDS = (
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
        "d1_zeta_b",
        "d2_zeta_b",
        "disc_alpha_b",
        "dd1_dT_b",
    )

    @staticmethod
    def _normal_cdf(value):
        """Return the standard normal CDF for a finite numeric input."""
        if not math.isfinite(value):
            raise ValueError("normal CDF input must be finite")
        return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))

    def execute(self, inputs):
        """Validate the runtime packet and compute the Option B put price."""
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a dict keyed by input port name")

        if self._INPUT_PORT not in inputs:
            raise ValueError(f"missing required input port: {self._INPUT_PORT}")

        option_b_params = inputs[self._INPUT_PORT]
        if not isinstance(option_b_params, dict):
            raise ValueError(f"inputs['{self._INPUT_PORT}'] must be a dict")

        missing_fields = [
            field for field in self._REQUIRED_FIELDS if field not in option_b_params
        ]
        if missing_fields:
            raise ValueError(
                f"{self._INPUT_PORT} missing required fields: "
                + ", ".join(sorted(missing_fields))
            )

        spot_b = option_b_params["spot_b"]
        strike_b = option_b_params["strike_b"]
        disc_alpha_b = option_b_params["disc_alpha_b"]
        d1_zeta_b = option_b_params["d1_zeta_b"]
        d2_zeta_b = option_b_params["d2_zeta_b"]

        try:
            negative_nd1 = self._normal_cdf(-d1_zeta_b)
            negative_nd2 = self._normal_cdf(-d2_zeta_b)
            put_price_b = strike_b * disc_alpha_b * negative_nd2 - spot_b * negative_nd1
        except (OverflowError, ValueError, TypeError) as exc:
            raise ValueError(f"failed to compute Option B put price: {exc}") from exc

        if not math.isfinite(put_price_b):
            raise ValueError("computed put_price_b must be finite")

        output = dict(option_b_params)
        output["put_price_b"] = put_price_b
        return {self._OUTPUT_PORT: output}


def build_component():
    """Build the generated component instance expected by the AC14 runtime."""
    return GeneratedComponent()
