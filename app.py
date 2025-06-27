import gradio as gr
import numpy as np
import time
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

from integral_tool.integral import (
    point_source_wavefield,
    fresnel_hologram,
    fresnel_hologram_scipy,
    fresnel_hologram_cpp,
    amplitude_phase,
)
from integral_tool.io import load_points_from_obj

def np_to_image(arr, cmap='gray'):
    """Convert a NumPy array to a PNG image for Gradio."""
    fig, ax = plt.subplots()
    ax.imshow(arr, cmap=cmap)
    ax.axis('off')
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

def process_hologram(obj_file, method):
    """
    Process the uploaded .obj file and compute the hologram.
    """
    if obj_file is None:
        raise gr.Error("Please upload a .obj file.")

    try:
        points = load_points_from_obj(obj_file.name)
        # Assign uniform brightness
        brightness = np.full(points.shape[0], 255.0)
        amplitude = point_source_wavefield(points, brightness)
    except Exception as e:
        raise gr.Error(f"Failed to process .obj file: {e}")

    grid = np.linspace(-0.05, 0.05, 128) # Use a slightly higher resolution for better visuals
    
    start_time = time.time()
    if method == "python":
        U = fresnel_hologram(points, amplitude, grid, grid)
    elif method == "scipy":
        U = fresnel_hologram_scipy(points, amplitude, grid, grid)
    elif method == "cpp":
        U = fresnel_hologram_cpp(points, amplitude, grid, grid)
    else:
        raise gr.Error(f"Unknown method: {method}")
    
    duration = time.time() - start_time
    
    A, phi = amplitude_phase(U)

    amp_image = np_to_image(A, cmap='viridis')
    phase_image = np_to_image(phi, cmap='twilight')

    return amp_image, phase_image, f"{duration:.3f} seconds"

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Huygens-Fresnel Hologram Generator")
    gr.Markdown(
        "Upload a `.obj` file containing point sources to compute and visualize "
        "the resulting holographic amplitude and phase."
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            obj_input = gr.File(label=".obj File", file_types=[".obj"])
            method_input = gr.Radio(
                ["python", "scipy", "cpp"], label="Computation Method", value="cpp"
            )
            submit_btn = gr.Button("Generate Hologram")
        
        with gr.Column(scale=2):
            time_output = gr.Textbox(label="Computation Time")
            with gr.Row():
                amplitude_output = gr.Image(label="Amplitude")
                phase_output = gr.Image(label="Phase")

    gr.Examples(
        examples=[["tests/sample.obj", "cpp"]],
        inputs=[obj_input, method_input],
        outputs=[amplitude_output, phase_output, time_output],
        fn=process_hologram,
        cache_examples=True,
    )

    submit_btn.click(
        fn=process_hologram,
        inputs=[obj_input, method_input],
        outputs=[amplitude_output, phase_output, time_output],
    )

if __name__ == "__main__":
    demo.launch()