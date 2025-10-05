# in Ubuntu-Hybrid
mkdir -p ~/documind-engineering/{infra,logs,models,data/docs,data/staging,scripts,notebooks}
mkdir -p ~/documind-engineering/src/{DocuMind.Host.Api,DocuMind.Common,python/{services,ingest,tests}}

cd ~/documind-engineering/src
dotnet new sln -n DocuMind
dotnet new web -n DocuMind.Host.Api
dotnet new classlib -n DocuMind.Common
dotnet sln DocuMind.sln add DocuMind.Host.Api/ DocuMind.Common/
dotnet add DocuMind.Host.Api/ reference DocuMind.Common/

# minimal packages (add others as we wire features)
cd DocuMind.Host.Api
dotnet add package Microsoft.AspNetCore.OpenApi
dotnet add package Qdrant.Client --version 1.9.0
dotnet add package Polly
dotnet add package Serilog.AspNetCore
dotnet add package K4os.Hash.xxHash
