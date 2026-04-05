"""AC14 generated component for computing zeta-corrected Option B vega."""

import math


class GeneratedComponent:
    """Compute zeta-corrected vega for Option B from precomputed d-params."""

    _INPUT_PORT = "option_b_params_output"
    _OUTPUT_PORT = "option_b_vega_output"
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
    _NUMERIC_FIELDS = tuple(field for field in _REQUIRED_FIELDS if field != "case_id")

    def execute(self, inputs):
        """Execute the packet contract using plain dict inputs and outputs."""
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a dict keyed by port name")
        if self._INPUT_PORT not in inputs:
            raise ValueError(f"missing required input port: {self._INPUT_PORT}")

        params = inputs[self._INPUT_PORT]
        if not isinstance(params, dict):
            raise ValueError(f"input port {self._INPUT_PORT} must contain a dict")

        missing_fields = [field for field in self._REQUIRED_FIELDS if field not in params]
        if missing_fields:
            raise ValueError(
                "missing required input fields for option_b_params_output: "
                + ", ".join(missing_fields)
            )

        case_id = params["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("case_id must be a non-empty string")

        numeric_values = {}
        for field_name in self._NUMERIC_FIELDS:
            numeric_values[field_name] = self._as_number(params[field_name], field_name)

        if numeric_values["T_b"] < 0.0:
            raise ValueError("T_b must be non-negative to compute vega_b")
        if numeric_values["zeta_b"] < 0.0:
            raise ValueError("zeta_b must be non-negative to compute vega_b")

        normal_pdf_d1 = self._standard_normal_pdf(numeric_values["d1_zeta_b"])
        vega_b = (
            numeric_values["spot_b"]
            * normal_pdf_d1
            * math.sqrt(numeric_values["T_b"])
            * math.sqrt(numeric_values["zeta_b"])
        )

        output = dict(params)
        output["vega_b"] = vega_b
        return {self._OUTPUT_PORT: output}

    @staticmethod
    def _as_number(value, field_name):
        """Validate that the provided field is a real numeric value."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a real number")
        return float(value)

    @staticmethod
    def _standard_normal_pdf(value):
        """Return the standard normal probability density at the given value."""
        return math.exp(-0.5 * value * value) / math.sqrt(2.0 * math.pi)


def build_component():
    """Build the generated AC14 component."""
    return GeneratedComponent()
