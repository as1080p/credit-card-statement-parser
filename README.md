💳 Credit Card Statement PDF Parser
===================================

A robust Python-based tool to extract structured data from credit card statement PDFs across multiple Indian banks.

🚀 Features
-----------

*   📄 Parses **credit card statement PDFs**
    
*   🏦 Supports multiple banks:
    
    *   HDFC Bank
        
    *   ICICI Bank
        
    *   State Bank of India (SBI)
        
    *   Bank of Baroda (BoB)
        
    *   Axis Bank
        
*   🔍 Automatically detects:
    
    *   Bank name
        
    *   Card variant (via fuzzy matching)
        
    *   Last 4 digits of card
        
*   📊 Extracts:
    
    *   Billing cycle
        
    *   Statement date
        
    *   Payment due date
        
    *   Total & minimum due
        
    *   Credit & cash limits
        
*   📑 Extracts transaction tables into structured format
    
*   💾 Outputs:
    
    *   JSON summary (outputs/json/)
        
    *   CSV transactions (outputs/csv/)
        

🛠️ Tech Stack
--------------

*   Python 3.x
    
*   pdfplumber – PDF text & table extraction
    
*   regex – pattern matching
    
*   rapidfuzz – fuzzy string matching
    
*   pandas – data handling
    
*   tabulate – CLI table display
    

📁 Project Structure
--------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   .├── parser.py├── outputs/│   ├── csv/│   │   └── transactions.csv│   └── json/│       └── _summary.json└── README.md   `

⚙️ Installation
---------------

### 1\. Clone the repository

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   git clone https://github.com/your-username/credit-card-parser.gitcd credit-card-parser   `

### 2\. Install dependencies

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install pdfplumber rapidfuzz pandas tabulate   `

▶️ Usage
--------

Run the parser:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python parser.py   `

Enter the path to your PDF when prompted:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   Enter path to statement PDF: sample_statements/icici_statement.pdf   `

📤 Output
---------

### ✅ JSON Summary

Stored in:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   outputs/json/_summary.json   `

Example:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "bank_detected": "ICICI Bank",    "card_variant": "Amazon Pay ICICI Bank Credit Card",    "last4": "3009",    "billing_cycle": "21 Jun 2025 to 20 Jul 2025",    "payment_due_date": "07 Aug 2025",    "total_balance": "12530.00",    "transactions_extracted": 5}   `

### 📊 Transactions CSV

Stored in:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   outputs/csv/transactions.csv   `

DateDescriptionAmountPage21 Jun 2025Sample Merchant 1150.751

🧠 How It Works
---------------

### 1\. Bank Detection

Uses keyword + fuzzy matching to identify the bank.

### 2\. Card Detection

Matches statement text against predefined card variants using rapidfuzz.

### 3\. Field Extraction

Uses regex to extract:

*   Dates
    
*   Amounts
    
*   Limits
    

### 4\. Transaction Extraction

*   Detects tables using pdfplumber
    
*   Identifies columns heuristically:
    
    *   Date
        
    *   Description
        
    *   Amount
        

🧪 Testing
----------

You can test using:

*   Real bank statements
    
*   Synthetic PDFs (recommended for development)
    

⚠️ Limitations
--------------

*   Depends on PDF structure (table extraction may fail for scanned PDFs)
    
*   Regex patterns may need tuning for new statement formats
    
*   OCR not supported (yet)
    

🔮 Future Improvements
----------------------

*   🧾 OCR support (Tesseract)
    
*   🤖 ML-based layout detection
    
*   📊 Dashboard visualization
    
*   🌐 Web UI for upload & parsing
    
*   📦 Batch processing
    

🤝 Contributing
---------------

Contributions are welcome!

1.  Fork the repo
    
2.  Create a new branch
    
3.  Commit your changes
    
4.  Submit a PR
    

📜 License
----------

This project is for educational and personal use.(Add a license here if you plan to open-source it publicly)

👩‍💻 Author
------------

Built with caffeine and chaos by **Anagha** ⚡(aka the "PDF whisperer" who made banks spill their secrets 😌)