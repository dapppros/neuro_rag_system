import os
import time
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track

# Initialize
load_dotenv()
console = Console()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class NeuroRAG:
    def __init__(self):
        self.model_name = "gemini-1.5-flash"
        self.uploaded_files = []
        self.books_dir = "books"
    
    def get_existing_cloud_files(self):
        """Creates a dictionary of files already uploaded to Google to avoid duplicates."""
        console.print("[italic grey]Checking Google Cloud for existing files...[/italic grey]")
        return {f.display_name: f for f in genai.list_files()}

    def ingest_books_folder(self):
        """Scans the books/ folder and syncs it with Gemini."""
        if not os.path.exists(self.books_dir):
            os.makedirs(self.books_dir)
            console.print(f"[yellow]Created directory: {self.books_dir}. Please put PDFs here![/yellow]")
            return

        # 1. Find local PDFs
        local_pdfs = glob.glob(os.path.join(self.books_dir, "*.pdf"))
        if not local_pdfs:
            console.print(f"[yellow]No PDFs found in {self.books_dir}/[/yellow]")
            return

        # 2. Get Cloud Files (to check for duplicates)
        cloud_files = self.get_existing_cloud_files()

        console.print(f"\n[bold blue]Syncing {len(local_pdfs)} book(s)...[/bold blue]")

        # 3. Iterate through local files
        for pdf_path in local_pdfs:
            filename = os.path.basename(pdf_path)
            
            if filename in cloud_files:
                # A. File already exists in Cloud -> Just reference it
                console.print(f"   [green]✔ Found in cloud:[/green] {filename}")
                self.uploaded_files.append(cloud_files[filename])
            else:
                # B. File is new -> Upload it
                self.upload_single_file(pdf_path, filename)

        console.print(f"[bold green]System Ready! {len(self.uploaded_files)} book(s) loaded.[/bold green]\n")

    def upload_single_file(self, file_path, display_name):
        console.print(f"   [bold yellow]⬆ Uploading:[/bold yellow] {display_name}...")
        try:
            # Upload with a specific display_name so we can find it later
            file_ref = genai.upload_file(file_path, display_name=display_name)
            
            # Wait for processing
            while file_ref.state.name == "PROCESSING":
                time.sleep(2)
                file_ref = genai.get_file(file_ref.name)
                
            if file_ref.state.name == "FAILED":
                console.print(f"   [bold red]❌ Failed:[/bold red] {display_name}")
            else:
                console.print(f"   [bold green]✔ Uploaded:[/bold green] {display_name}")
                self.uploaded_files.append(file_ref)
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    def query_system(self, user_question):
        if not self.uploaded_files:
            console.print("[red]No textbooks loaded![/red]")
            return

        console.print(f"\n[bold yellow]Thinking...[/bold yellow]")

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"temperature": 0.2, "top_p": 0.95, "top_k": 64}
        )

        request_content = [user_question] + self.uploaded_files

        try:
            response = model.generate_content(request_content)
            console.print("\n[bold cyan]--- Answer ---[/bold cyan]")
            console.print(Markdown(response.text))
            console.print("[bold cyan]--------------[/bold cyan]\n")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

def main():
    rag = NeuroRAG()
    
    console.print("[bold purple]Welcome to the Neurophysiology RAG System[/bold purple]")
    
    # AUTOMATIC LOADING ON STARTUP
    rag.ingest_books_folder()
    
    console.print("Type 'ask <question>' to ask a question.")
    console.print("Type 'refresh' to re-scan the books folder.")
    console.print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Command: ").strip()
        
        if user_input.lower() == 'exit':
            break
        
        elif user_input.lower() == 'refresh':
            rag.uploaded_files = [] # Clear current list
            rag.ingest_books_folder()
            
        elif user_input.startswith("ask "):
            question = user_input[4:].strip()
            rag.query_system(question)
            
        else:
            console.print("[grey]Unknown command.[/grey]")

if __name__ == "__main__":
    main()