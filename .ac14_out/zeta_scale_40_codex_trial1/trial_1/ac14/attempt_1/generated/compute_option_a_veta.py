"""Compute the zeta-modified veta for Option A."""

import math


class GeneratedComponent:
    """Execute the packet-local veta computation with strict validation."""

    _INPUT_PORT = "option_a_params_output"
    _OUTPUT_PORT = "option_a_veta_output"
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
        "d1_zeta_a",
        "d2_zeta_a",
        "disc_alpha_a",
        "dd1_dT_a",
    )

    def execute(self, inputs):
        """Validate inputs, compute veta, and return the packet output dict."""
        params = self._require_port(inputs, self._INPUT_PORT)
        payload = {}
        for field_name in self._REQUIRED_FIELDS:
            payload[field_name] = params[field_name]

        spot_a = self._require_number(params, "spot_a")
        zeta_a = self._require_number(params, "zeta_a")
        d1_zeta_a = self._require_number(params, "d1_zeta_a")
        dd1_dT_a = self._require_number(params, "dd1_dT_a")
        time_to_expiry = self._require_number(params, "T_a")

        if time_to_expiry <= 0.0:
            raise ValueError("option_a_params_output['T_a'] must be greater than 0")
        if zeta_a < 0.0:
            raise ValueError("option_a_params_output['zeta_a'] must be non-negative")

        sqrt_time = math.sqrt(time_to_expiry)
        sqrt_zeta = math.sqrt(zeta_a)
        normal_pdf = math.exp(-0.5 * d1_zeta_a * d1_zeta_a) / math.sqrt(2.0 * math.pi)

        veta_a = (
            spot_a
            * sqrt_zeta
            * normal_pdf
            * ((1.0 / (2.0 * sqrt_time)) - (d1_zeta_a * dd1_dT_a))
        )

        if not math.isfinite(veta_a):
            raise ValueError("computed veta_a is not finite")

        payload["veta_a"] = veta_a
        return {self._OUTPUT_PORT: payload}

    def _require_port(self, inputs, port_name):
        """Return a required input payload after checking the packet shape."""
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a dict keyed by port name")
        if port_name not in inputs:
            raise ValueError(f"missing required input port: {port_name}")
        port_payload = inputs[port_name]
        if not isinstance(port_payload, dict):
            raise ValueError(f"input port '{port_name}' must contain a dict payload")
        missing_fields = [name for name in self._REQUIRED_FIELDS if name not in port_payload]
        if missing_fields:
            raise ValueError(
                f"input port '{port_name}' is missing required fields: {', '.join(missing_fields)}"
            )
        return port_payload

    def _require_number(self, payload, field_name):
        """Return a finite numeric field value from the payload."""
        value = payload[field_name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"option_a_params_output['{field_name}'] must be a number")
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            raise ValueError(f"option_a_params_output['{field_name}'] must be finite")
        return numeric_value


def build_component():
    """Construct the generated component instance expected by the runtime."""
    return GeneratedComponent()
