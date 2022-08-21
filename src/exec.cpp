
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>
#include <sstream>
#include <cmath>

enum Ukaz
{
    JUMP,
    JMPD,
    JMPC,
    PUSH,
    POP,
    POS,
    ZERO,
    LOAD,
    LDOF,
    TOP,
    SOFF,
    LOFF,
    STOR,
    STOF,
    PRTN,
    PRTS,
    ADD,
    SUB,
    MUL,
    DIV,
    MOD,
    POW,
};

const char *imena[] = {
    "JUMP",
    "JMPD",
    "JMPC",
    "PUSH",
    "POP ",
    "POS ",
    "ZERO",
    "LOAD",
    "LDOF",
    "TOP ",
    "SOFF",
    "LOFF",
    "STOR",
    "STOF",
    "PRTN",
    "PRTS",
    "ADD ",
    "SUB ",
    "MUL ",
    "DIV ",
    "MOD ",
    "POW ",
};

union Podatek
{
    int i;
    float f;
    char c[4];
};

struct UkazPodatek
{
    Ukaz ukaz;
    Podatek podatek;
};

#define RESNICA 1.0f
#define LAZ 0.0f

using namespace std;

ostream &operator<<(ostream &str, vector<Podatek> stack)
{
    if (stack.empty()) return str;
    str << '[' << stack[0].f;
    for (int i = 1; i < stack.size(); i++) {
        str << ", " << stack[i].f;
    }
    str << ']';
    return str;
}


void run(vector<UkazPodatek> &program, bool print_stack)
{
    vector<Podatek> stack;
    stack.reserve(256);

    int pc = 0;
    int addroff = 0;

    while (pc < program.size())
    {
        UkazPodatek &ukaz = program[pc];

        switch (ukaz.ukaz)
        {
        case JUMP:
            pc = ukaz.podatek.i;
            break;
        case JMPD:
            pc = stack.back().i - 1;
            stack.pop_back();
            break;
        case JMPC:
            if (stack.back().i != LAZ)
                pc = ukaz.podatek.i;
            stack.pop_back();
            break;
        case PUSH:
            stack.push_back(ukaz.podatek);
            break;
        case POP:
            stack.pop_back();
            break;
        case POS:
            stack.back().f = (stack.back().f > 0) ? RESNICA : LAZ;
            break;
        case ZERO:
            stack.back().f = (stack.back().f == 0) ? RESNICA : LAZ;
            break;
        case LOAD:
            stack.push_back(stack[ukaz.podatek.i]);
            break;
        case LDOF:
            stack.push_back(stack[ukaz.podatek.i + addroff]);
            break;
        case TOP:
            addroff = stack.size() + ukaz.podatek.i;
            break;
        case SOFF:
            addroff = stack.back().i;
            stack.pop_back();
            break;
        case LOFF:
            stack.push_back(Podatek { addroff });
            break;
        case STOR:
            stack[ukaz.podatek.i] = stack.back();
            stack.pop_back();
            break;
        case STOF:
            stack[ukaz.podatek.i + addroff] = stack.back();
            stack.pop_back();
            break;
        case PRTN:
            if (!print_stack)
                cout << stack.back().f;
            stack.pop_back();
            break;
        case PRTS: 
            {
                char *top = stack.back().c;
                if (!print_stack) {
                    if (top[0] != '\0') cout << top[0];
                    if (top[1] != '\0') cout << top[1];
                    if (top[2] != '\0') cout << top[2];
                    if (top[3] != '\0') cout << top[3];
                }
            }
            stack.pop_back();
            break;
        case ADD:
            stack.end()[-2].f = stack.end()[-2].f + stack.end()[-1].f;
            stack.pop_back();
            break;
        case SUB:
            stack.end()[-2].f = stack.end()[-2].f - stack.end()[-1].f;
            stack.pop_back();
            break;
        case MUL:
            stack.end()[-2].f = stack.end()[-2].f * stack.end()[-1].f;
            stack.pop_back();
            break;
        case DIV:
            stack.end()[-2].f = stack.end()[-2].f / stack.end()[-1].f;
            stack.pop_back();
            break;
        case MOD:
            stack.end()[-2].f = fmod(stack.end()[-2].f, stack.end()[-1].f);
            stack.pop_back();
            break;
        case POW:
            stack.end()[-2].f = pow(stack.end()[-2].f, stack.end()[-1].f);
            stack.pop_back();
            break;
        }

        if (print_stack) {
            printf("%3d | ", pc);

            switch (program[pc].ukaz)
            {
            case PUSH:
                cout << imena[program[pc].ukaz] << ' ' << program[pc].podatek.f << ": ";
                break;
            case LDOF:
            case STOF:
                cout << imena[program[pc].ukaz] << ' ' << addroff 
                << (program[pc].podatek.i >= 0 ? "+" : "") << program[pc].podatek.i<< ": ";
                break;
            case TOP:
                cout << imena[program[pc].ukaz] << ' ' 
                <<  (program[pc].podatek.i >= 0 ? "+" : "") << program[pc].podatek.i<< ": ";
                break;

            default:
                cout << imena[program[pc].ukaz] << ' ' << program[pc].podatek.i << ": ";
                break;
            }
        }

        if (print_stack)
            cout << stack << '\n';
        pc++;
    }
}

int main(int argc, char **argv)
{
    if (argc != 2 && argc != 3)
        return 1;

    vector<UkazPodatek> program;
    program.reserve(64);

    bool print_stack = false;

    for (int i = 1; i < argc - 1; i++) {
        if (strcmp(argv[i], "-s") == 0) {
            print_stack = true;
            break;
        }
    }

    ifstream file;
    string vrstica;

    file.open(argv[argc-1], ios::in);

    while (getline(file, vrstica))
    {
        if (vrstica == "")
            // prazna vrstica
            continue;

        string ukaz, ostanek;
        istringstream besede(vrstica);

        besede >> ukaz;

        if (print_stack)
            cout << program.size() << ' ' << vrstica << '\n';

        if (ukaz[0] == '#') {
            // komentar
            continue;
        }
        else if (ukaz == "JUMP") {
            // samo absolutni skoki
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ JUMP, stoi(ostanek) - 1 });
        }
        else if (ukaz == "JMPD") {
            program.push_back({ JMPD });
        }
        else if (ukaz == "JMPC") {
            // samo absolutni skoki
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ JMPC, stoi(ostanek) - 1 });
        }
        else if (ukaz == "PUSH") {
            ostanek = vrstica.substr(ukaz.length()+1);
            char &tip = ostanek[0];
            if (tip == '#') {
                // literal
                Podatek podatek;

                if (ostanek.find('.') != string::npos)
                    podatek.f = stof(ostanek.substr(1));
                else
                    podatek.i = stoi(ostanek.substr(1));

                program.push_back({ PUSH, podatek });
            }
            else if (tip == '"') {
                // 4 chars
                Podatek chars = { 0 }; 
                int n = 0;
                for (int i = 1; ostanek[i] != '"'; i++) {
                    if (ostanek[i] == '\\') {
                        switch (ostanek[i+1])
                        {
                        case 'n':
                            chars.c[n++] = '\n';
                            break;
                        case 'r':
                            chars.c[n++] = '\r';
                            break;
                        case 't':
                            chars.c[n++] = '\t';
                            break;
                        }
                        i++;
                    }
                    else {
                        chars.c[n++] = ostanek[i];
                    }
                }
                program.push_back({ PUSH, chars });
            }
        }
        else if (ukaz == "LOAD") {
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ LOAD, stoi(ostanek) });
        }
        else if (ukaz == "LDOF") {
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ LDOF, stoi(ostanek) });
        }
        else if (ukaz == "STOR") {
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ STOR, stoi(ostanek) });
        }
        else if (ukaz == "STOF") {
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ STOF, stoi(ostanek) });
        }
        else if (ukaz == "TOP") {
            ostanek = vrstica.substr(ukaz.length()+1);
            program.push_back({ TOP, stoi(ostanek) });
        }
        else if (ukaz == "LOFF") {
            program.push_back({ LOFF });
        }
        else if (ukaz == "SOFF") {
            program.push_back({ SOFF });
        }
        else if (ukaz == "PRTN") {
            program.push_back({ PRTN });
        }
        else if (ukaz == "PRTS") {
            program.push_back({ PRTS });
        }
        else if (ukaz == "POP") {
            program.push_back({ POP });
        }
        else if (ukaz == "POS") {
            program.push_back({ POS });
        }
        else if (ukaz == "ZERO") {
            program.push_back({ ZERO });
        }
        else if (ukaz == "ADD") {
            program.push_back({ ADD });
        }
        else if (ukaz == "SUB") {
            program.push_back({ SUB });
        }
        else if (ukaz == "MUL") {
            program.push_back({ MUL });
        }
        else if (ukaz == "DIV") {
            program.push_back({ DIV });
        }
        else if (ukaz == "MOD") {
            program.push_back({ MOD });
        }
        else if (ukaz == "POW") {
            program.push_back({ POW });
        }
        else {
            cerr << "Nepričakovan ukaz: " << ukaz << '\n';
            throw exception();
        }
    }

    run(program, print_stack);
}
