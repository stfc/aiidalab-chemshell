"""Defines the MVC model for computational resource configuration for AiiDA."""

import traitlets as tl


class ComputationalResourcesModel(tl.HasTraits):
    """Model for the resource setup stage."""

    code_label = tl.Unicode("").tag(sync=True)
    ncpus = tl.Int(4).tag(sync=True)
    process_label = tl.Unicode("").tag(sync=True)
    process_description = tl.Unicode("").tag(sync=True)
    submitted = tl.Bool(False).tag(sync=True)

    default_guide = """
        <p>
            Configure the computational resources required to run the ChemShell
            calculation. Additionally, you can provide a label and description for
            the AiiDA process that will be created.
        </p>
    """

    def validate(self) -> bool:
        """
        Validate the model's inputs.

        Returns
        -------
        bool
            True if all inputs are valid, False otherwise.
        """
        if not self.code_label:
            print("ERROR: No code selected.")
            return False
        return True
