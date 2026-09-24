import os
from huggingface_hub import InferenceClient
from agent.tool import Tool


def generate_image(prompt: str):

    api_key = os.getenv("HUGGINGFACE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "HUGGINGFACE_API_KEY is not set."
        )

    try:
        client = InferenceClient(
            provider="auto",
            api_key=api_key
        )

        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )

        output_dir = "Image_output"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(
            output_dir,
            "generated_image.png"
        )

        image.save(output_path)

        return {
            "success": True,
            "output_path": output_path,
            "message": "Image generated successfully."
        }

    except Exception as e:
        raise RuntimeError(
            f"Image generation failed: {str(e)}"
        )


image_generator_tool = Tool(
    name="image_generator",
    description="Generate an image from a text prompt.",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed description of the image to generate."
            }
        },
        "required": ["prompt"]
    },
    function=generate_image
)