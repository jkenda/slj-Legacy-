
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
    JMPC,
    PUSH,
    POP,
    POS,
    ZERO,
    LOAD,
    STORE,
    PRINTN,
    PRINTS,
    ADD,
    SUB,
    MUL,
    DIV,
    MOD,
    POW,
};

const char *imena[] = {
    "JUMP  ",
    "JMPC  ",
    "PUSH  ",
    "POP   ",
    "POS   ",
    "ZERO  ",
    "LOAD  ",
    "STORE ",
    "PRINTN",
    "PRINTS",
    "ADD   ",
    "SUB   ",
    "MUL   ",
    "DIV   ",
    "MOD   ",
    "POW   ",
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

    uint_fast64_t pc = 0;

    while (pc < program.size())
    {
        UkazPodatek &ukaz = program[pc];

        if (print_stack) 
            cout << imena[program[pc].ukaz] << ": ";

        switch (ukaz.ukaz)
        {
        case JUMP:
            pc = ukaz.podatek.i;
            break;
        case JMPC:
            if (stack.back().f == RESNICA)
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
        case STORE:
            stack[ukaz.podatek.i] = stack.back();
            stack.pop_back();
            break;
        case PRINTN:
            if (!print_stack)
                cout << stack.back().f;
            stack.pop_back();
            break;
        case PRINTS: 
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
            {
                float &b = stack.back().f; stack.pop_back();
                float &a = stack.back().f;
                stack.back().f = a + b;
            }
            break;
        case SUB:
            {
                float &b = stack.back().f; stack.pop_back();
                float &a = stack.back().f;
                stack.back().f = a - b;
            }
            break;
        case MUL:
            {
                float &b = stack.back().f; stack.pop_back();
                float &a = stack.back().f;
                stack.back().f = a * b;
            }
            break;
        case DIV:
            {
                float &b = stack.back().f; stack.pop_back();
                float &a = stack.back().f;
                stack.back().f = a / b;
            }
            break;
        case MOD:
            {
                float &b = stack.back().f; stack.pop_back();
                float &a = stack.back().f;
                stack.back().f = fmod(a, b);
            }
            break;
        case POW:
            {
                float &b = stack.back().f; stack.pop_back();
                float &a = stack.back().f;
                stack.back().f = pow(a, b);
            }
            break;
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

        if (ukaz[0] == '#') {
            // komentar
            continue;
        }
        else if (ukaz == "JUMP") {
            // samo absolutni skoki
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ JUMP, stoi(ostanek) - 1 });
        }
        else if (ukaz == "JMPC") {
            // samo absolutni skoki
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ JMPC, stoi(ostanek) - 1 });
        }
        else if (ukaz == "POS") {
            program.push_back({ POS });
        }
        else if (ukaz == "ZERO") {
            program.push_back({ ZERO });
        }
        else if (ukaz == "PUSH") {
            ostanek = vrstica.substr(ukaz.length()+1);
            char &tip = ostanek[0];
            if (tip == '#') {
                // literal
                Podatek podatek;
                podatek.f = stof(ostanek.substr(1));
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
        else if (ukaz == "POP") {
            program.push_back({ POP });
        }
        else if (ukaz == "LOAD") {
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ LOAD, stoi(ostanek) });
        }
        else if (ukaz == "STORE") {
            ostanek = vrstica.substr(ukaz.length()+2);
            program.push_back({ STORE, stoi(ostanek) });
        }
        else if (ukaz == "PRINTN") {
            program.push_back({ PRINTN });
        }
        else if (ukaz == "PRINTS") {
            program.push_back({ PRINTS });
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
            throw exception();
        }
    }

    run(program, print_stack);
}
