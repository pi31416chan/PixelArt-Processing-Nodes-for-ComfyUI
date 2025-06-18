import torch
import torch.nn.functional as F


class PixelArtDownscaleTargetSizeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "target_w": ("INT", {"default": 1024, "min": 1, "max": 4096, "step": 1}),
                "target_h": ("INT", {"default": 1024, "min": 1, "max": 4096, "step": 1}),
                "method": (["nearest", "lanczos"],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "downscale_image"

    CATEGORY = "Image/Processing"

    def downscale_image(self, image, target_w, target_h, method):
        """
        Downscale or upscale the image based on the scale factor.
        :param image: The input image tensor [batch, height, width, channels].
        :param target_w: Target width of the resulting image size.
        :param target_h: Target height of the resulting image size.
        :param method: 'nearest' for nearest-neighbor, 'lanczos' for Lanczos resampling.
        :return: Scaled image tensor.
        """

        # Ensure image is on the GPU for processing
        image = image.to(torch.device("cuda"))

        # Choose interpolation method based on input
        if method == "nearest":
            interpolation = "nearest"
        elif method == "lanczos":
            interpolation = "bicubic"  # PyTorch uses 'bicubic' for high-quality resampling similar to Lanczos.

        # Calculate new dimensions
        _, height, width, _ = image.shape
        new_height = target_w
        new_width = target_h

        # Ensure valid dimensions
        if new_height <= 0 or new_width <= 0:
            raise ValueError("Invalid scaling factor resulting in zero or negative dimensions.")

        # Resize the image using the selected method
        resized_image = F.interpolate(image.permute(0, 3, 1, 2), size=(new_height, new_width), mode=interpolation)

        # Return the resized image in the format [batch, height, width, channels]
        return (resized_image.permute(0, 2, 3, 1),)
