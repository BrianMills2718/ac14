"""AC14 generated component for computing the Option B speed output."""

import math


class GeneratedComponent:
    """Compute the zeta-modified Option B speed and return the declared packet."""

    _PARAMS_INPUT_PORT = "option_b_params_output"
    _GAMMA_INPUT_PORT = "option_b_gamma_output"
    _OUTPUT_PORT = "option_b_speed_output"
    _PARAMS_REQUIRED_FIELDS = (
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
    _GAMMA_REQUIRED_FIELDS = _PARAMS_REQUIRED_FIELDS + ("gamma_b",)

    @staticmethod
    def _require_packet(inputs, port_name):
        """Return a required input packet or raise a loud validation error."""
        if port_name not in inputs:
            raise ValueError(f"missing required input port: {port_name}")
        packet = inputs[port_name]
        if not isinstance(packet, dict):
            raise ValueError(f"inputs['{port_name}'] must be a dict")
        return packet

    @staticmethod
    def _require_fields(packet, port_name, field_names):
        """Raise when a packet is missing any required schema fields."""
        missing_fields = [field for field in field_names if field not in packet]
        if missing_fields:
            raise ValueError(
                f"{port_name} missing required fields: "
                + ", ".join(sorted(missing_fields))
            )

    @staticmethod
    def _require_numeric(packet, field_name):
        """Return a finite numeric field value or raise a loud validation error."""
        value = packet[field_name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be numeric")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"{field_name} must be finite")
        return value

    def _validate_shared_fields(self, option_b_params, option_b_gamma):
        """Raise when the two upstream packets disagree on shared fields."""
        for field_name in self._PARAMS_REQUIRED_FIELDS:
            params_value = option_b_params[field_name]
            gamma_value = option_b_gamma[field_name]
            if isinstance(params_value, (int, float)) and isinstance(
                gamma_value, (int, float)
            ):
                params_numeric = float(params_value)
                gamma_numeric = float(gamma_value)
                if not math.isfinite(params_numeric) or not math.isfinite(gamma_numeric):
                    raise ValueError(f"{field_name} must be finite in both input packets")
                if not math.isclose(
                    params_numeric,
                    gamma_numeric,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    raise ValueError(
                        f"input packets disagree on shared field {field_name}"
                    )
            elif params_value != gamma_value:
                raise ValueError(f"input packets disagree on shared field {field_name}")

    def execute(self, inputs):
        """Validate the runtime packet and compute the Option B speed."""
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a dict keyed by input port name")

        option_b_params = self._require_packet(inputs, self._PARAMS_INPUT_PORT)
        option_b_gamma = self._require_packet(inputs, self._GAMMA_INPUT_PORT)

        self._require_fields(
            option_b_params,
            self._PARAMS_INPUT_PORT,
            self._PARAMS_REQUIRED_FIELDS,
        )
        self._require_fields(
            option_b_gamma,
            self._GAMMA_INPUT_PORT,
            self._GAMMA_REQUIRED_FIELDS,
        )
        self._validate_shared_fields(option_b_params, option_b_gamma)

        spot_b = self._require_numeric(option_b_params, "spot_b")
        vol_b = self._require_numeric(option_b_params, "vol_b")
        t_b = self._require_numeric(option_b_params, "T_b")
        d1_zeta_b = self._require_numeric(option_b_params, "d1_zeta_b")
        gamma_b = self._require_numeric(option_b_gamma, "gamma_b")

        if spot_b <= 0.0:
            raise ValueError("spot_b must be > 0 for speed denominator")
        if vol_b <= 0.0:
            raise ValueError("vol_b must be > 0 for speed denominator")
        if t_b <= 0.0:
            raise ValueError("T_b must be > 0 for speed denominator")

        sqrt_t_b = math.sqrt(t_b)
        denominator_term = vol_b * sqrt_t_b
        if denominator_term == 0.0:
            raise ValueError("vol_b*sqrt(T_b) must be non-zero")

        try:
            speed_b = -gamma_b * (1.0 + d1_zeta_b / denominator_term) / spot_b
        except (OverflowError, ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"failed to compute Option B speed: {exc}") from exc

        if not math.isfinite(speed_b):
            raise ValueError("computed speed_b must be finite")

        output = dict(option_b_params)
        output["speed_b"] = float(speed_b)
        return {self._OUTPUT_PORT: output}


def build_component():
    """Build the generated component instance expected by the AC14 runtime."""
    return GeneratedComponent()
