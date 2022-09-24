FROM debian:latest

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y \
    sudo \
    wine \
    wine32 \
    git \
    python3 python3-pip \
    wget && \
    apt-get clean && \
    cd /tmp/ && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN adduser --system --group --uid 1000 appuser && usermod -aG sudo appuser

RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo 'set completion-ignore-case on' >> ~/.inputrc && \
    echo "export LS_OPTIONS='--color=auto'" >> ~/.bashrc && \
    echo "alias ls='ls $LS_OPTIONS'" >> ~/.bashrc

USER appuser
